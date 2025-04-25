from typing import List, Optional
import numpy as np
import pandas as pd

from algorithms.algorithm import Algorithm
from algorithms.hmm import HMMRegimeModel
from configs.path import PathConfig
from errors.base_exception import BacktesterError
from pipeline.feature_loader import FeatureLoader
from pipeline.indicators import AdjustedReturnRate, Volatility
from pipeline.features import Feature
from strategies.position_sizer.base_position_sizer import BasePositionSizer

class HMMPositionSizer(BasePositionSizer):
    """Automatic adjust position sizing based on market regime."""
    
    def __init__(self, backtestEndDate: str, data: Optional[pd.DataFrame] = None, loader: Optional[FeatureLoader] = None, lookBackPeriod: int = 30, tradeFees: float = 0.0006):

        self.data = data
        self.loader = loader if loader is not None else FeatureLoader(backtestDate=backtestEndDate)
        self.backtestEndDate = backtestEndDate
        
        self.selectedFeatures: List[str] = ["daily_return", "log_volatility"]
        self.features: List[Feature] = None
        
        self.lookBackPeriod = lookBackPeriod
        self.tradeFees = tradeFees

        self.initializeStrategy()

    def initializeStrategy(self, train: bool = False):

        self.features = [
            AdjustedReturnRate(tradeFees=self.tradeFees),
            Volatility(windowSize=self.lookBackPeriod)
        ]
        dataWithFeatures = self.loader.loadFeatures(data = self.data, features=self.features)
        dataWithFeatures.dropna(inplace=True)

        dataWithFeatures.to_csv(f"{PathConfig.FEATURES_DIR}/hmm_features.csv")

        self.data = dataWithFeatures

        if self.data is None:
            raise BacktesterError("strategy/data-not-loaded")
    
        self._initializeModel(self.data[self.selectedFeatures], train=train)
        
    def retrainModel(self, data: pd.DataFrame):
        self.data = data
        self.initializeStrategy(train=True)

    def calculatePositionSize(self, orderDate: str, availableCash: float):

        if not self.model.isFitted:
            raise BacktesterError("algorithm/model-not-fitted")
        
        if self.data is None:
            raise BacktesterError("strategy/data-not-loaded")
        
        if "regimes" not in self.data.columns:
            raise BacktesterError("feature/missing-columns", details="Column name not found: regimes")

        if self.data.loc[orderDate]["regimes"] == 3:
            positionSize = 0.8
        
        elif self.data.loc[orderDate]["regimes"] == 4:
            positionSize = 0.6
        
        elif self.data.loc[orderDate]["regimes"] == 2:
            positionSize = 0.4
        
        elif self.data.loc[orderDate]["regimes"] == 1:
            positionSize = 0.2
        
        else:
            positionSize = 0.05

        return availableCash * positionSize

    def _initializeModel(self, data, train=False):

        self.model: Algorithm = HMMRegimeModel()

        if train or not self.model.isFitted:
            self.model.fit(data.loc[:self.backtestEndDate][self.selectedFeatures], optimize=True)  # Train until the backtest end date

        regimes = self.model.predict(data)  # Predict the regimes for all the features
        data = data.copy()
        data["regimes"] = regimes
        print(data.groupby("regimes").mean())

        self.data = data