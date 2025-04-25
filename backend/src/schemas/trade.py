from datetime import datetime
import pandas as pd
from pydantic import BaseModel
from typing import Dict, List, Optional, Tuple, Any

from schemas.order import Order
from schemas.position import Position, Positions

class TradeMetrics(BaseModel):
    totalReturn: float = 0.0   # Total returns in USD
    totalReturnPct: float = 0.0  # Total returns in percentage
    finalEquity: float = 0.0   # Final equity in USD
    annualizedReturn: float = 0.0  # Annualized returns in percentage
    annualizedVolatility: float = 0.0   # Annualized volatility in percentage
    sharpeRatio: float = 0.0
    sortinoRatio: float = 0.0
    calmarRatio: float = 0.0
    maxDrawdown: float = 0.0
    backtestDuration: int = 0  # Backtest duration in days

class TradeStatistic(BaseModel):
    averagePnl: float = 0.0   # Average profit and loss for the trades
    profitableTrades: int = 0   # Winning / Profitable trades
    losingTrades: int = 0
    winRate: float = 0.0
    totalTrades: int = 0

class TradePortfolio(BaseModel):
    initialCapital: float = None
    peakEquity: float = initialCapital
    startDate: str = None
    endDate: str = None
    equityOnCash: float = initialCapital
    positions: Positions = Positions()
    tradeHistory: List[Order] = None
    equityCurves: List[Tuple[datetime, float]] = None
    drawdownCurves: List[Tuple[datetime, float]] = None
    results: TradeMetrics
    tradeStatistics: TradeStatistic
