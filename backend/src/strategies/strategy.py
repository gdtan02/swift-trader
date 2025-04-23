import pandas as pd
from abc import ABC, abstractmethod
from typing import Optional

from algorithms.algorithm import Algorithm


class BaseStrategy(ABC):
    """Abstract base class for all trading strategies"""

    @abstractmethod
    def initializeStrategy(self):
        """Load the data necessary for the algorithm."""
        pass
        
    @abstractmethod
    def generateSignals(self) -> pd.Series:
        """Generate the trade signals (BUY = 1, SELL = -1, HOLD = 0)"""
        pass
