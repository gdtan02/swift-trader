
from typing import List, Union
import numpy as np
import pandas as pd

from pipeline.features import Feature
from errors.base_exception import BacktesterError


class AdjustedReturnRate(Feature):
    """
    Adjusted return rate: The net return in percentage.
    """
    def __init__(self, tradeFees: float = 0.0006):
        self.tradeFees = tradeFees

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate adjusted return rate based on close price."""
        resultData = data.copy()

        if "close" not in resultData.columns:
            raise BacktesterError(
                "feature/missing-columns", 
                details=f"'close' is required to compute 'adjusted_return_rate'")
        
        resultData["daily_return"] = resultData["close"].pct_change()
        resultData["log_return"] = np.log(resultData["close"] / resultData["close"].shift(1))
        # resultData["adjusted_return_rate"] = resultData["daily_return"] - self.tradeFees

        return resultData
    
class Volatility(Feature):
    """Calculate volatility based on rolling window standard deviation."""
    def __init__(self, windowSize: Union[List[int], int]):
        self.windowSize = windowSize

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate volatility based on close price."""
        resultData = data.copy()

        if "close" not in resultData.columns:
            raise BacktesterError(
                "feature/missing-columns", 
                details=f"'close' is required to compute 'volatility'")
        
        returns = resultData["close"].pct_change()

        if type(self.windowSize) == int:
            resultData["volatility"] = returns.rolling(window=self.windowSize).std()
            resultData[f"log_volatility"] = np.log(resultData[f"volatility"])
        else:
            for window in self.windowSize:
                resultData[f"volatility_{window}"] = returns.rolling(window=window).std()
                resultData[f"log_volatility_{window}"] = np.log(resultData[f"volatility_{window}"])

        return resultData