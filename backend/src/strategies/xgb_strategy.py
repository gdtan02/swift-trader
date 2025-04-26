from typing import List, Optional
import numpy as np
import pandas as pd

from algorithms.algorithm import Algorithm
from algorithms.xgboost import XGBModel
from configs.path import PathConfig
from errors.base_exception import BacktesterError
from pipeline.feature_loader import FeatureLoader
from pipeline.features import Feature
from strategies.strategy import BaseStrategy

class XGBoostStrategy(BaseStrategy):
    """Generate alpha signals using XGBoost model to predict Bitcoin's price movement in the future."""
    
    def __init__(self, forecastHorizon: int = 6, threshold: float = 0.3):

        if threshold < 0 or threshold > 1.0:
            raise BacktesterError("strategy/invalid-threshold", details="Threshold value for XGBoost model should between 0 and 1.")
        

        self.forecastHorizon = forecastHorizon
        self.threshold = threshold
        self.model = XGBModel()
        self.features = ["nrpl", "nvt", "nul", "ema_30", "nupl", "vwap", "bollinger_lower", "target"]

    # def initializeStrategy(self, data, train: bool = False):

    #     loadedData = self.loader.loadFeatures(data = self.data, features = [])

    #     loadedData = self._createTargetVariable(loadedData, self.forecastHorizon)

    #     loadedData.dropna(inplace=True)

    #     loadedData.to_csv(f"{PathConfig.FEATURES_DIR}/xgb_features.csv")

    #     self.data = loadedData

    #     if self.data is None:
    #         raise BacktesterError("strategy/data-not-loaded")
        
    #     self._initializeModel(self.data[self.selectedFeatures], train=train)


    def createFeaturesAndTargetVariable(self, df: pd.DataFrame):

        resultDf = df.copy()
        resultDf = self.calculate_ema(resultDf)
        resultDf = self.calculate_vwap(resultDf)
        resultDf = self.calculate_bollinger_bandswidth(resultDf)

        # Create target
        df["futureReturns"] = (df["close"].shift(-self.forecastHorizon) - df["close"]) / df["close"]

        upper = df["futureReturns"].quantile(1 - self.threshold)
        lower = df["futureReturns"].quantile(self.threshold)

        resultDf["target"] = 1  # HOLD
        resultDf.loc[df["futureReturns"] > upper, "target"] = 2  # BUY signal
        resultDf.loc[df["futureReturns"] < lower, "target"] = 0  # SELL signal

        print("resultDf=", resultDf.head())
        return resultDf

    def generateSignals(self, data: Optional[pd.DataFrame], train: bool = False):

        print("data=", data)

        X = data.drop(columns="target")
        y = data["target"]
        
        if train:
            self.model.fit(X, y)

        if not self.model.is_fitted:
            raise BacktesterError("algorithm/model-not-fitted")
        
        signals = self.model.predict(X)
        return signals - 1
        

    def calculate_ema(self, df, period=30):
        df[f"ema_{period}"] = df["close"].ewm(span=period, adjust=False).mean()
        return df

    def calculate_vwap(self, df):
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        df['vwap'] = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
        return df

    def calculate_bollinger_bandswidth(self, df):
        df = df.copy()

        sma = df["close"].rolling(window=20).mean()
        std_dev = df["close"].rolling(window=20).std()

        df["bollinger_upper"] = sma + 2 * std_dev
        df["bollinger_lower"] = sma - 2 * std_dev
        df["bb_width"] = (df["bollinger_upper"] - df["bollinger_lower"]) / sma
        return df
        
    # def _initializeModel(self, data, train=False):
        
    #     self.model: Algorithm = XGBModel()

    #     X = data.drop(columns='target')
    #     y = data["target"]

    #     print("y=", y.unique())
        
    #     if train or not self.model.is_fitted:

    #         X_train = X[:self.backtestEndDate]
    #         y_train = y[:self.backtestEndDate]

    #         print("y_train =", y_train.unique())

    #         self.model.fit(X=X_train, y=y_train, optimize=True)

    #     probabilities = self.model.predict_proba(X)
    #     print(f"probabilities = {probabilities}")