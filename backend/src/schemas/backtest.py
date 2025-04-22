from typing import Optional
from pydantic import BaseModel, field_validator
from enum import Enum

from errors.base_exception import BacktesterError

class RuntimeMode(str, Enum):
    BACKTEST = "backtest"
    LIVE_TRADE = "live-trade"

class EntryExitStrategy(str, Enum):
    MEAN_REVERSION = "mean-reversion"
    TREND_FOLLOWING = "trend-following"
    SL_TP = "stoploss-takeprofit"

class BacktestRequestModel(BaseModel):
    runtimeMode: Optional[str] = None
    entryExitLogic: Optional[str] = None

    @field_validator("runtimeMode")
    def checkRuntimeMode(cls, v) -> str:
        if v is not None and v not in RuntimeMode:
            raise BacktesterError("backtest/invalid-runtime-mode")
        return v
    
    @field_validator("entryExitLogic")
    def checkEntryExitLogic(cls, v) -> str:
        if v is not None and v not in EntryExitStrategy:
            raise BacktesterError("backtest/invalid-entry-exit-logic")
        return v

class BacktestResponseModel(BaseModel):
    backtestResult: float = 1.0