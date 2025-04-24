from typing import Dict, List, Optional, Union, Any

from strategies.strategy import BaseStrategy
from schemas.backtest import BacktestRequestModel, BacktestResponseModel


class BacktesterService:
    """Backtester engine"""

    def __init__(self):
        pass

    async def run(self, settings: BacktestRequestModel) -> BacktestResponseModel:
        
        self.initializeBacktesterSettings(settings)

    def initializeBacktesterSettings(self, settings: BacktestRequestModel):
        self.mode = settings.runtimeMode
        self.strategyName = settings.strategyName
        self.startDate = settings.startDate
        self.endDate = settings.endDate
        self.allowForwardTest = settings.allowForwardTest
        self.forwardStartDate = settings.forwardStartDate
        self.forwardEndDate = settings.forwardEndDate
        self.allowPermutation = settings.allowPermutation
        self.entryExitLogic = settings.entryExitMode
        self.positionSizingMode = settings.positionSizingMode
        
    def initializeStrategy(self, strategyName: str) -> BaseStrategy:
        pass
        