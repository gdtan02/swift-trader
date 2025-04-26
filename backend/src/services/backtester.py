from datetime import datetime
from typing import Dict, List, Optional, Union, Any

import pandas as pd

from pipeline.features import Feature
from pipeline.indicators import AdjustedReturnRate, Volatility
from strategies.xgb_strategy import XGBoostStrategy
from schemas.order import Order, OrderSide, OrderStatus
from configs.path import PathConfig
from metrics.metric import Metric
from schemas.position import Positions
from errors.base_exception import BacktesterError
from pipeline.feature_loader import FeatureLoader
from strategies.position_sizer import BasePositionSizer, FixedProportionPositionSizer, HMMPositionSizer
from strategies.strategy import BaseStrategy
from schemas.backtest import BacktestRequestModel, BacktestResponseModel, EntryExitStrategy, PositionSizingMode
from schemas.trade import TradePortfolio, TradeMetrics, TradeStatistic


class BacktesterService:
    """Backtester engine"""

    def __init__(self):
        self.backtestMarketData = None
        self.forwardTestMarketData = None
        self.backtestPortfolio = None
        self.forwardTestPortfolio = None

    def run(self, settings: BacktestRequestModel) -> BacktestResponseModel:
        
        self.initializeBacktesterSettings(settings)

        # Load data
        priceData = self.featureLoader.loadMarketPriceData()

        if self.startDate < priceData.index.min() or self.endDate > priceData.index.max():
            raise BacktesterError("backtest/date-interval-out-of-range") 

        backtestPriceData = priceData.loc[self.startDate:self.endDate]

        # Initialize strategy and generate signals
        self.fullData = self.featureLoader.loadFullData()        
        self.initializeStrategy(strategyName=self.strategyName, fullData=self.fullData)
        
        self.backtestPortfolio = self.simulateTrade(self.features[self.startDate: self.endDate], backtestPriceData, backtest=True)

        if self.allowForwardTest:

            if self.forwardStartDate < priceData.index.min() or self.forwardEndDate > priceData.index.max():
                raise BacktesterError("backtest/date-interval-out-of-range") 

            forwardTestPriceData = priceData.loc[self.forwardStartDate:self.forwardEndDate]
            self.forwardTestPortfolio = self.simulateTrade(self.features[self.forwardStartDate:self.forwardEndDate], forwardTestPriceData, backtest=False)

        print("Backtest Portfolio: ", self.backtestPortfolio, "ForwardTest Portfolio: ", self.forwardTestPortfolio)

        return BacktestResponseModel(
            backtestResult=self.backtestPortfolio.results,
            backtestStatistics=self.backtestPortfolio.tradeStatistics,
            forwardTestResult=self.forwardTestPortfolio.results,
            forwardTestStatistics=self.forwardTestPortfolio.tradeStatistics
        )

        
    def simulateTrade(self, features: pd.DataFrame, data: pd.DataFrame, backtest: bool = False) -> TradePortfolio:

        if self.entryExitLogic not in EntryExitStrategy:
            raise BacktesterError("backtest/invalid-entry-exit-logic")
        
        self.initializePositionSizingModel(
            positionSizeMode=self.positionSizingMode, 
            proportion=self.maxPositionSize,
            data=self.fullData,
            train=backtest)

        # Initialize portfolio settings
        portfolio = TradePortfolio(
            initialCapital = self.initialCapital,
            peakEquity = self.initialCapital,
            startDate = str(data.index.min()),
            endDate = str(data.index.max()),
            equityOnCash = self.initialCapital,
            positions = Positions(),
            tradeHistory = [],
            equityCurves = [],
            drawdownCurves = [],
            results = TradeMetrics(),
            tradeStatistics = TradeStatistic()
        )

        # Generate positions based on the signals 
        tradeSimulator = pd.DataFrame(index = data.index)
        tradeSimulator["price"] = data["close"]
        tradeSimulator["priceChange"] = data["close"].pct_change().fillna(0.0)
        tradeSimulator["signals"] = self.strategy.generateSignals(features, train=backtest)

        if self.entryExitLogic == EntryExitStrategy.TREND_FOLLOWING:
            tradeSimulator["position"] = tradeSimulator["signals"].replace(0, pd.NA).ffill().fillna(0) # Fowardfill previous position (LONG or SHORT)
            tradeSimulator["trades"] = abs(tradeSimulator["position"].diff()).fillna(abs(tradeSimulator["position"]))  
        elif self.entryExitLogic == EntryExitStrategy.MEAN_REVERSION:
            tradeSimulator["position"] = tradeSimulator["signals"].copy()
            tradeSimulator["trades"] = abs(tradeSimulator["position"].diff()).fillna(abs(tradeSimulator["position"]))

        equityHistory = []
        # Execute trades
        for i in range(len(tradeSimulator)):
            currentTime = tradeSimulator.index[i]
            currentPrice = tradeSimulator.iloc[i]["price"]

            trade = tradeSimulator.iloc[i]["trades"]
            position = tradeSimulator.iloc[i]["position"]

            if trade > 0:
                if position == 1:  # LONG
                    positionSize = self.positionSizeModel.calculatePositionSize(currentTime, portfolio.equityOnCash)
                    commissionFee = self._calculateOrderCommission(positionSize)

                    # Create BUY order
                    order = Order(
                        timestamp = currentTime,
                        orderType = "market",
                        orderSide = "buy",
                        price = currentPrice,
                        quantity = (positionSize - commissionFee) / currentPrice,
                        commissionFee = commissionFee
                    )
                    order = self._executeOrder(order, currentPrice, currentTime, portfolio=portfolio)

                    # Update portfolio
                    portfolio.positions.updatePosition(order)
                    portfolio.equityOnCash -= positionSize
                    portfolio.tradeHistory.append((currentTime, order))
                    
                elif position == -1:  # SHORT
                    sellableShare = portfolio.positions.getPosition("btc").quantity
                    sellAmount = sellableShare * currentPrice
                    commissionFee = self._calculateOrderCommission(sellAmount)

                    # Create SELL order
                    order = Order(
                        timestamp = currentTime,
                        orderType = "market",
                        orderSide = "sell",
                        price = currentPrice,
                        quantity = sellableShare,
                        commissionFee = commissionFee
                    )
                    order = self._executeOrder(order, currentPrice, currentTime, portfolio=portfolio)

                    # Update portfolio
                    portfolio.positions.updatePosition(order)
                    portfolio.equityOnCash += (sellAmount - commissionFee)
                    portfolio.tradeHistory.append((currentTime, order))

            currentEquity = portfolio.equityOnCash + portfolio.positions.getTotalEquityValue(currentPrice=currentPrice)
            equityHistory.append(currentEquity)

            if currentEquity > portfolio.peakEquity:
                portfolio.peakEquity = currentEquity

            currentDrawdown = (currentEquity - portfolio.peakEquity) / portfolio.peakEquity

            
            portfolio.equityCurves.append((currentTime, currentEquity))
            portfolio.drawdownCurves.append((currentTime, currentDrawdown))


        tradeSimulator["equity"] = equityHistory
        tradeSimulator["drawdown"] = (tradeSimulator["equity"] - tradeSimulator["equity"].cummax()) / tradeSimulator["equity"].cummax()
        tradeSimulator["pnl"] = tradeSimulator["equity"].diff().fillna(0)

        print("Trade simulator: ", tradeSimulator)
        tradeSimulator.to_csv(f"{PathConfig.FEATURES_DIR}/trade_simulator.csv")

        # Convert into tuple formats and save into portfolio
        portfolio = self._calculateMetrics(portfolio, tradeSimulator)
                
        return portfolio

    def initializeBacktesterSettings(self, settings: BacktestRequestModel):
        self.mode = settings.runtimeMode
        self.strategyName = settings.strategyName
        self.startDate = settings.startDate
        self.endDate = settings.endDate
        self.initialCapital = settings.initialCapital
        self.commissionRate = settings.commissionRate
        self.minCommission = settings.minCommission
        self.allowForwardTest = settings.allowForwardTest
        self.forwardStartDate = settings.forwardStartDate
        self.forwardEndDate = settings.forwardEndDate
        self.allowPermutation = settings.allowPermutation
        self.entryExitLogic = settings.entryExitMode
        self.positionSizingMode = settings.positionSizingMode
        self.maxPositionSize = settings.maxPositionSize

        if self.forwardEndDate is not None:
            self.featureLoader = FeatureLoader(startDate=settings.startDate, endDate=self.forwardEndDate)
        else:
            self.featureLoader = FeatureLoader(startDate=settings.startDate, endDate=settings.endDate)
        self.strategy: Optional[BaseStrategy] = None
        self.positionSizeModel: Optional[BasePositionSizer] = None
        
        
    def initializeStrategy(self, strategyName: str, fullData: pd.DataFrame) -> BaseStrategy:
        if strategyName == 'xgb':
            self.strategy = XGBoostStrategy()
            print("strategy loaded=", self.strategy)
            self.features = self.strategy.createFeaturesAndTargetVariable(fullData)
            self.features = self.features[self.strategy.features]
        elif strategyName == "cnn":
            pass

        else:
            raise BacktesterError("backtest/strategy-not-found")
        

    def initializePositionSizingModel(self, positionSizeMode: PositionSizingMode = PositionSizingMode.FIXED, proportion: Optional[float] = 0.5, data: Optional[pd.DataFrame] = None, train: bool = False) -> BasePositionSizer:

        if positionSizeMode == PositionSizingMode.FIXED:
            self.positionSizeModel = FixedProportionPositionSizer(proportion=proportion)

        elif positionSizeMode == PositionSizingMode.AUTO:
            self.positionSizeModel = HMMPositionSizer(
                backtestEndDate=self.endDate,
                lookBackPeriod=30)
            hmmFeatures: List[Feature] = [
                AdjustedReturnRate(tradeFees=self.positionSizeModel.tradeFees),
                Volatility(windowSize=self.positionSizeModel.lookBackPeriod)
            ]
            self.hmmFeatures = self.featureLoader.loadFeatures(data, hmmFeatures)
            self.positionSizeModel.initializeStrategy(self.hmmFeatures, train=train)
        
        else:
            raise BacktesterService("backtest/invalid-position-sizing-model")
        
        return self.positionSizeModel
    
    def _executeOrder(self, order: Order, executionPrice: float = None, executionTimestamp: datetime = None, portfolio: TradePortfolio = None) -> Order:
        if order.orderSide == OrderSide.BUY:
            if executionPrice * order.quantity > portfolio.equityOnCash:
                # Reject order for insufficient cash.
                order.status = OrderStatus.REJECTED
                order.cancelReason = "Insufficient cash."
                return
            
            order.status = OrderStatus.COMPLETED
            order.executionPrice = executionPrice
            order.executionTimestamp = executionTimestamp

        elif order.orderSide == OrderSide.SELL:
            
            order.status = OrderStatus.COMPLETED
            order.executionPrice = executionPrice
            order.executionTimestamp = executionTimestamp

            avgEntryPrice = portfolio.positions.getPosition("btc").avgEntryPrice
            order.calculatePnl(avgEntryPrice)

        return order



    def _calculateOrderCommission(self, tradeAmount: float):
        return max(self.commissionRate * tradeAmount, self.minCommission)
    
    def _calculateMetrics(self, portfolio: TradePortfolio, tradeRecords: pd.DataFrame):
        tradeMetrics = Metric(portfolio=portfolio, tradeRecords=tradeRecords)
        portfolio.results = tradeMetrics.getResults()
        portfolio.tradeStatistics = tradeMetrics.getTradeStatistics()

        return portfolio