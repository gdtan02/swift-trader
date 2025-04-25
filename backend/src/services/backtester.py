from datetime import datetime
from typing import Dict, List, Optional, Union, Any

import pandas as pd

from schemas.order import Order, OrderSide, OrderStatus
from configs.path import PathConfig
from metrics.metric import Metric
from schemas.position import Position, Positions
from errors.base_exception import BacktesterError
from pipeline.feature_loader import FeatureLoader
from strategies.position_sizer import BasePositionSizer, FixedProportionPositionSizer, HMMPositionSizer
from strategies.strategy import BaseStrategy
from schemas.backtest import BacktestRequestModel, BacktestResponseModel, EntryExitStrategy, PositionSizingMode
from schemas.trade import TradePortfolio, TradeMetrics


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
        data = self.featureLoader.loadMarketData()

        if self.startDate < data.index.min() or self.endDate > data.index.max():
            raise BacktesterError("backtest/date-interval-out-of-range") 

        backtestMarketData = data.loc[self.startDate:self.endDate]
        self.backtestPortfolio = self.simulateTrade(backtestMarketData)

        if self.allowForwardTest:

            if self.forwardStartDate < data.index.min() or self.forwardEndDate > data.index.max():
                raise BacktesterError("backtest/date-interval-out-of-range") 

            forwardTestMarketData = data.loc[self.forwardStartDate:self.forwardEndDate]
            self.forwardTestPortfolio = self.simulateTrade(forwardTestMarketData)

        print("Backtest Portfolio: ", self.backtestPortfolio, "ForwardTest Portfolio: ", self.forwardTestPortfolio)

        
    def simulateTrade(self, data: pd.DataFrame) -> TradePortfolio:

        if self.entryExitLogic not in EntryExitStrategy:
            raise BacktesterError("backtest/invalid-entry-exit-logic")

        # Initialize strategy and generate signals
        self.strategy = self.initializeStrategy(strategyName=self.strategyName)
        
        # Initialize portfolio settings
        portfolio = TradePortfolio(
            initialCapital = self.initialCapital,
            peakEquity = self.initialCapital,
            startDate = str(data.index.min()),
            endDate = str(data.index.max()),
            equityOnCash = self.initialCapital,
            positions = Positions(),
            returns = [],
            tradeHistory = [],
            equityCurves = [],
            drawdownHistory = [],
            results = TradeMetrics()
        )

        # Generate positions based on the signals 
        tradeSimulator = pd.DataFrame(index = data.index)
        tradeSimulator["price"] = data["close"]
        tradeSimulator["priceChange"] = data["close"].pct_change().fillna(0.0)
        tradeSimulator["signals"] = self.strategy.generateSignals(data)

        if self.entryExitLogic == EntryExitStrategy.TREND_FOLLOWING:
            tradeSimulator["position"] = tradeSimulator["signals"].replace(0, pd.NA).ffill().fillna(0) # Fowardfill previous position (LONG or SHORT)
            tradeSimulator["trades"] = abs(tradeSimulator["position"].diff()).fillna(abs(tradeSimulator["position"]))  
        elif self.entryExitLogic == EntryExitStrategy.MEAN_REVERSION:
            tradeSimulator["position"] = tradeSimulator["signals"].copy()
            tradeSimulator["trades"] = abs(tradeSimulator["position"].diff()).fillna(abs(tradeSimulator["position"]))

        print("Trade simulator: ", tradeSimulator)
        tradeSimulator.to_csv(f"{PathConfig.FEATURES_DIR}/trade_simulator.csv")

        equityHistory = []
        # Execute trades
        for i in range(len(tradeSimulator)):
            currentTime = tradeSimulator.iloc[i].index
            currentPrice = tradeSimulator.iloc[i]["price"]

            trade = tradeSimulator.iloc[i]["trades"]
            position = tradeSimulator.iloc[i]["position"]

            if trade > 0:
                if position == 1:  # LONG
                    positionSize = self.positionSizeModel.calculatePositionSize(portfolio.equityOnCash)
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

            currentEquity = portfolio.equityOnCash + portfolio.positions.getTotalEquityValue()
            equityHistory.append(currentEquity)

            if currentEquity > portfolio.peakEquity:
                portfolio.peakEquity = currentEquity

            currentDrawdown = (currentEquity - portfolio.peakEquity) / portfolio.peakEquity

            portfolio.tradeHistory.append((currentTime, order))
            portfolio.equityCurves.append((currentTime, currentEquity))
            portfolio.drawdownCurves.append((currentTime, currentDrawdown))


        tradeSimulator["equity"] = equityHistory
        tradeSimulator["drawdown"] = (tradeSimulator["equity"] - tradeSimulator["equity"].cummax()) / tradeSimulator["equity"].cummax()
        tradeSimulator["pnl"] = tradeSimulator["equity"].diff().fillna(0)

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

        self.featureLoader = FeatureLoader(backtestDate=self.endDate)
        self.strategy: Optional[BaseStrategy] = None
        self.positionSizeModel: Optional[BasePositionSizer] = None

        self.initializePositionSizingModel(
            positionSizeMode=self.positionSizingMode, 
            proportion=settings.maxPositionSize)
        
        
    def initializeStrategy(self, strategyName: str) -> BaseStrategy:
        pass
        

    def initializePositionSizingModel(self, positionSizeMode: PositionSizingMode = PositionSizingMode.FIXED, proportion: Optional[float] = 1.0) -> BasePositionSizer:

        if positionSizeMode == PositionSizingMode.FIXED:
            self.positionSizeModel = FixedProportionPositionSizer(proportion=proportion)

        elif positionSizeMode == PositionSizingMode.AUTO:
            self.positionSizeModel = HMMPositionSizer(
                backtestEndDate=self.endDate, 
                loader=self.featureLoader,
                lookBackPeriod=30)
        
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