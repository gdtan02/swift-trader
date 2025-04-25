import numpy as np
import pandas as pd
from typing import List, Optional

from schemas.order import Order, OrderSide
from schemas.trade import TradePortfolio, TradeMetrics, TradeStatistic

class Metric:

    def __init__(self, portfolio: TradePortfolio, tradeRecords: pd.DataFrame):

        self.initialCapital = portfolio.initialCapital
        self.orders = portfolio.tradeHistory
        self.returns = tradeRecords['returns']
        self.equityValues = tradeRecords['equity']
        self.drawdownValues = tradeRecords['drawdown']
        self.totalTradingDays = len(self.equityValues) / 365.0
        self.results: TradeMetrics = TradeMetrics(
            totalReturn =self.totalReturn(),
            totalReturnPct = self.totalReturnInPct(),
            finalEquity = self.equityValues.iloc[-1],
            annualizedReturn = self.annualizedReturn(),
            annualizedVolatility = self.annualizedVolatility(),
            sharpeRatio = self.sharpeRatio(),
            sortinoRatio = self.sortinoRatio(),
            maxDrawdown = self.maxDrawdown(),
            calmarRatio = self.calmarRatio(),
            backtestDuration = self.totalTradingDays
        )
        self.tradeStatistics: TradeStatistic = self.getTradeStatistics()

    def getResults(self) -> TradeMetrics:
        return self.results
    
    def getTradeStatistics(self) -> TradeStatistic:
        return self.tradeStatistics

    def totalReturn(self):
        return self.equityValues.iloc[-1] - self.initialCapital
    
    def totalReturnInPct(self):
        return (self.equityValues.iloc[-1] - self.initialCapital) / self.initialCapital

    def annualizedReturn(self):
        """Compound Annual Growth Rate"""
        totalReturnPct = self.totalReturnInPct()
        return np.power((1 + totalReturnPct), 252 / self.totalTradingDays) - 1
    
    def annualizedVolatility(self):
        """Standard deviation of returns"""
        return self.returns.std() * np.sqrt(252)
    
    def sharpeRatio(self):
        annualizedReturn = self.annualizedReturn()
        annualizedVolatility = self.annualizedVolatility()
        return annualizedReturn / annualizedVolatility if annualizedVolatility > 0 else None
    
    def sortinoRatio(self):
        downsideReturns = self.returns[self.returns < 0]
        downsideDeviation = downsideReturns.std() * np.sqrt(252) if len(downsideReturns) > 0 else 0
        return self.returns.mean() / downsideDeviation if downsideDeviation > 0 else None

    def maxDrawdown(self):
        return self.drawdownValues.min()

    def calmarRatio(self):
        mdd = abs(self.maxDrawdown())
        return self.annualizedReturn() / mdd if mdd != 0 else None
    
    def adjustedReturns(self):
        """Adjusted returns for trading fees (0.06% per trade)"""
        return self.returns * (1 - 0.0006)
    
    def getTradeStatistics(self) -> TradeStatistic:

        sellTrades: List[Order] = [order for order in self.orders if order.orderSide == OrderSide.SELL]
        profitableTrades = sum([1 for trade in sellTrades if trade.pnl > 0])
        losingTrades = sum([1 for trade in sellTrades if trade.pnl < 0])
        winRate = profitableTrades / len(sellTrades)
        avgTradePnl = pd.Series([order.pnl for order in sellTrades]).mean()

        stats: TradeStatistic = TradeStatistic(
            averagePnl=avgTradePnl,
            profitableTrades=profitableTrades,
            losingTrades=losingTrades,
            winRate=winRate,
            totalTrades=sellTrades
        )
        return stats



