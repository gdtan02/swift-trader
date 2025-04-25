from typing import Any, Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, ValidationInfo, field_validator
from enum import Enum
from datetime import date, datetime, timedelta

from schemas.trade import TradeMetrics
from errors.base_exception import BacktesterError

class RuntimeMode(str, Enum):
    BACKTEST = "backtest"
    LIVE_TRADE = "live-trade"

class EntryExitStrategy(str, Enum):
    MEAN_REVERSION = "mean-reversion"
    TREND_FOLLOWING = "trend-following"

class PositionSizingMode(str, Enum):
    FIXED = "fixed"  # fixed
    AUTO = "auto"  # use HMM

class BacktestRequestModel(BaseModel):
    strategyName: str
    startDate: str
    endDate: str
    initialCapital: float = 100000.0
    commissionRate: float = 0.0006  # 0.06 % by default
    minCommission: float = 0.0
    allowForwardTest: bool = False
    forwardStartDate: str = None
    forwardEndDate: str = None
    allowPermutation: bool = False
    assets: Optional[List[str]] = ["btc"]
    runtimeMode: Optional[str] = RuntimeMode.BACKTEST
    entryExitMode: Optional[str] = None
    positionSizingMode: Optional[str] = None
    maxPositionSize: Optional[float] = None
    stopLoss: Optional[float] = None
    takeProfit: Optional[float] = None

    @field_validator("endDate")
    def checkEndDateAfterStartDate(cls, v: Union[date, datetime], info: ValidationInfo) -> Union[date, datetime]:

        if info.data.get("startDate"):
            startDate = datetime.strptime(info.data.get("startDate"), "%Y-%m-%d %H:%M:%S")
            endDate = datetime.strptime(v, "%Y-%m-%d %H:%M:%S")

            if endDate < startDate:
                raise BacktesterError("backtest/invalid-date-interval", details="End date must be after start date.")
            
            if endDate - timedelta(days=365) < startDate:
                raise BacktesterError("backtest/invalid-date-interval", details="Should run the backtest for at least 1 year.")   
                
        return v

    @field_validator("runtimeMode")
    def checkRuntimeMode(cls, v) -> str:
        if v is not None and v not in RuntimeMode:
            raise BacktesterError("backtest/invalid-runtime-mode")
        
        return v
    
    @field_validator("entryExitMode")
    def checkEntryExitLogic(cls, v) -> Optional[str]:
        if v is not None and v not in EntryExitStrategy:
            raise BacktesterError("backtest/invalid-entry-exit-logic")
        
        return v
    
    @field_validator("positionSizingMode")
    def checkPositionSizingModel(cls, v) -> Optional[str]:
        if v is not None and v not in PositionSizingMode:
            raise BacktesterError("backtest/invalid-position-sizing-model")
        
        return v

    @field_validator("maxPositionSize", "stopLoss", "takeProfit")
    def checkRange(cls, v) -> Optional[float]:
        if v is not None and (v > 1.0 or v < 0.0):
            raise BacktesterError("backtest/invalid-range")
        
        return v


class BacktestResponseModel(BaseModel):
    backtestResult: Optional[TradeMetrics] = None
    forwardTestResult: Optional[TradeMetrics] = None