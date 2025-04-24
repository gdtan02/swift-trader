from typing import List
import numpy as np
import pandas as pd

from algorithms.algorithm import Algorithm
from algorithms.hmm import HMMRegimeModel
from pipeline.features import Feature
from strategies.position_sizer.base_position_sizer import BasePositionSizer

class HMMPositionSizer(BasePositionSizer):
    """Automatic adjust position sizing based on market regime."""
    
    def __init__(self, lookBackPeriod: int = 60):
        self.lookBackPeriod: int = lookBackPeriod
        self.model: Algorithm = HMMRegimeModel()
        self.selectedFeatures: List[str] = ["adjusted_return", "log_volatility"]
        self.features: List[Feature] = None
        self.df: pd.DataFrame = []

    def _trainModel(self):
        pass