from typing import Dict, List, Optional, Union, Any

from pipeline.feature_loader import FeatureLoader
from strategies.position_sizer import BasePositionSizer, FixedProportionPositionSizer, HMMPositionSizer
from strategies.strategy import BaseStrategy
from schemas.backtest import BacktestRequestModel, BacktestResponseModel, PositionSizingMode


class BacktesterService:
    """Backtester engine"""

    def __init__(self):
        pass

    async def run(self, settings: BacktestRequestModel) -> BacktestResponseModel:
        
        self.initializeBacktesterSettings(settings)

        if self.allowForwardTest:
            pass


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

        self.featureLoader = FeatureLoader(backtestDate=self.endDate)
        self.strategy: Optional[BaseStrategy] = None
        self.positionSizeModel: Optional[BasePositionSizer] = None

        self.initializeStrategy(strategyName=self.strategyName)

        self.initializePositionSizingModel(
            positionSizeMode=self.positionSizingMode, 
            proportion=settings.maxPositionSize)
        
    def initializeStrategy(self, strategyName: str) -> BaseStrategy:
        pass
        

    def initializePositionSizingModel(self, positionSizeMode: PositionSizingMode, proportion: Optional[float] = None) -> BasePositionSizer:

        if positionSizeMode == PositionSizingMode.FIXED:
            self.positionSizeModel = FixedProportionPositionSizer(proportion=proportion)

        elif positionSizeMode == PositionSizingMode.AUTO:
            self.positionSizeModel = HMMPositionSizer(
                backtestDate=self.endDate, 
                loader=self.featureLoader,
                lookBackPeriod=30)
        
        else:
            raise BacktesterService("backtest/invalid-position-sizing-model")
        
        return self.positionSizeModel