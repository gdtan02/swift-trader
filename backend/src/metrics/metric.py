import numpy as np
import pandas as pd
from typing import List, Optional

from schemas.order import Order, OrderSide
from schemas.trade import TradePortfolio, TradeMetrics, TradeStatistic

class Metric:
    
    HOURS_IN_YEAR = 365 * 24
    
    
    def __init__(self, portfolio: TradePortfolio, tradeRecords: pd.DataFrame):

        self.initialCapital = portfolio.initialCapital
        self.orders = portfolio.tradeHistory
        self.returns = tradeRecords['pnl']
        self.equityValues = tradeRecords['equity']
        self.drawdownValues = tradeRecords['drawdown']

        self.totalPeriods = len(self.returns)
        self.totalYears = len(self.equityValues) / self.HOURS_IN_YEAR
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
            backtestDuratioInYrs = self.totalYears
        )
        self.tradeStatistics: TradeStatistic = self.calculateTradeStatistics()

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
        return (self.equityValues.iloc[-1] / self.initialCapital) ** (1 / self.totalYears) - 1
    
    def annualizedVolatility(self):
        """Standard deviation of returns"""
        return self.returns.std() * np.sqrt(self.HOURS_IN_YEAR)
    
    def sharpeRatio(self):
        annualizedReturn = self.annualizedReturn()
        annualizedVolatility = self.annualizedVolatility()
        return annualizedReturn / annualizedVolatility if annualizedVolatility > 0 else None
    
    def sortinoRatio(self):
        downsideReturns = self.returns[self.returns < 0]
        downsideDeviation = downsideReturns.std() * np.sqrt(self.HOURS_IN_YEAR) if len(downsideReturns) > 0 else 0
        return self.annualizedReturn() / downsideDeviation if downsideDeviation > 0 else None

    def maxDrawdown(self):
        return self.drawdownValues.min() * 100

    def calmarRatio(self):
        mdd = abs(self.maxDrawdown())
        return self.annualizedReturn() / mdd if mdd != 0 else None
    
    def adjustedReturns(self):
        """Adjusted returns for trading fees (0.06% per trade)"""
        return self.returns * (1 - 0.0006)
    
    def calculateTradeStatistics(self) -> TradeStatistic:

        sellTrades: List[Order] = [order for _, order in self.orders if order.orderSide == OrderSide.SELL]
        pnl_list = [trade.pnl for trade in sellTrades]

        profitableTrades = sum(1 for trade in sellTrades if trade.pnl > 0)
        losingTrades = sum(1 for trade in sellTrades if trade.pnl < 0)
        totalTrades = len(pnl_list)
        winRate = profitableTrades / totalTrades if totalTrades > 0 else 0.0
        avgTradePnl = pd.Series(pnl_list).mean()

        stats: TradeStatistic = TradeStatistic(
            averagePnl=avgTradePnl,
            profitableTrades=profitableTrades,
            losingTrades=losingTrades,
            winRate=winRate,
            totalTrades=totalTrades
        )
        return stats



