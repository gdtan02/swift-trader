from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd


class Algorithm(ABC):
    """Abstract base class for all ML algorithms."""

    def __init__(self, **kwargs):
        self.params = kwargs
        self.isFitted = False

    @abstractmethod
    def fit(self, X, y=None):
        """Train the algorithm on the given data."""
        pass

    @abstractmethod
    def predict(self, X):
        """Generate predictions using the trained algorithms"""
        pass

    def saveModel(self, path: str):
        raise NotImplementedError("saveModel Not Implemented")
    
    def loadModel(self, path: str):
        raise NotImplementedError("loadModel Not Implemented")