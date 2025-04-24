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
    
    def __init__(self, backtestDate: str, loader: Optional[FeatureLoader] = None, lookBackPeriod: int = 30, tradeFees: float = 0.0006):
        self.loader = loader if loader is not None else FeatureLoader(backtestDate=backtestDate)
        self.backtestDate = backtestDate
        self.lookBackPeriod: int = lookBackPeriod
        self.model: Algorithm = HMMRegimeModel()
        self.selectedFeatures: List[str] = ["daily_return", "log_volatility"]
        self.features: List[Feature] = None
        self.lookBackPeriod = lookBackPeriod
        self.tradeFees = tradeFees
        self.df: pd.DataFrame = []

        self._initializeData()
        self._trainModel()

    def calculatePositionSize(self, orderDate: str, availableCash: float):

        if not self.model.isFitted:
            raise BacktesterError("algorithm/model-not-fitted")
        
        if self.df is None:
            raise BacktesterError("strategy/data-not-loaded")
        
        self.df["regimes"] = self.model.predict(self.df)
        print(self.df.groupby("regimes").mean())

        print("Order:", self.df.loc[orderDate])

        if self.df.loc[orderDate]["regimes"] == 3:
            positionSize = 0.8
        
        elif self.df.loc[orderDate]["regimes"] == 4:
            positionSize = 0.6
        
        elif self.df.loc[orderDate]["regimes"] == 2:
            positionSize = 0.4
        
        elif self.df.loc[orderDate]["regimes"] == 1:
            positionSize = 0.2
        
        else:
            positionSize = 0.05

        return availableCash * positionSize

    def _initializeData(self):
        self.features = [
            AdjustedReturnRate(tradeFees=self.tradeFees),
            Volatility(windowSize=self.lookBackPeriod)
        ]
        self.df = self.loader.loadFeatures(features=self.features)[self.selectedFeatures]
        print("Index", self.df.index)
        self.df.dropna(inplace=True)

        self.df.to_csv(f"{PathConfig.FEATURES_DIR}/hmm_features.csv")

    def _trainModel(self):
        if self.df is None:
            raise BacktesterError("strategy/data-not-loaded")
        
        if self.model.isFitted:
            return
        
        self.model.fit(X = self.df[:self.backtestDate], optimize=True)

    
        
        
    