from typing import List, Optional
from pathlib import Path
import os
import pandas as pd

from errors.base_exception import BacktesterError
from configs.path import PathConfig
from pipeline.features import Feature


class FeatureLoader:

    def __init__(self, startDate: str, endDate: str):
        """Initialize the feature loader."""
        self.startDate = startDate
        self.endDate = endDate
        self.rawDataPath: str = PathConfig.RAW_DATA_DIR
        self.featurePath: str = PathConfig.FEATURES_DIR

        self.exchangeFlowsPath = f"{self.rawDataPath}/cryptoquant_exchange_flows.csv"
        self.minerFlowsPath = f"{self.rawDataPath}/cryptoquant_miner_flows.csv"
        self.flowIndicatorPath = f"{self.rawDataPath}/cryptoquant_flow_indicator.csv"
        self.marketIndicatorPath = f"{self.rawDataPath}/cryptoquant_market_indicator.csv"
        self.networkIndicatorPath = f"{self.rawDataPath}/cryptoquant_network_indicator.csv"
        self.marketDataPath = f"{self.rawDataPath}/cryptoquant_market_data.csv"
        self.networkDataPath = f"{self.rawDataPath}/cryptoquant_network_data.csv" 
        self.data: pd.DataFrame = pd.DataFrame()

        self._loadAndMergeData()

    def loadFullData(self):
        """Load the full data."""
        if self.data is not None:
            return self.data
        
        else:
            raise BacktesterError("feature/fail-to-load-data")
        
    def loadFeatures(self, data: Optional[pd.DataFrame] = None, features: List[Feature] = None) -> pd.DataFrame:
        """Add the specified features into the DataFrame and return it."""
        if data is None:
            data = self.data
        
        if features is None:
            raise BacktesterError("feature/missing-features")
        
        resultData = data.copy()

        for feature in features:
            resultData = feature.transform(resultData)

        return resultData
    
    def loadMarketPriceData(self):
        """Load the market data (close price) only for the backtester to simulate trade."""
        if "close" not in self.data.columns:
            raise BacktesterError("feature/missing-columns")

        return self.data[["close"]]
    
    def _loadAndMergeData(self):
        """
        Read all the CSV raw data files and merge into a single dataframe for feature engineering.
        The dataset will be sliced on the backtestDate, the data beyond this date will not be used.
        Raise BacktesterError if the file path does not exist.
        """
        try:
            # Load the data if available 
            filePath = f"{self.rawDataPath}/cryptoquant_full_data.csv"

            self.data = pd.read_csv(filePath)
            self.data.set_index("datetime", inplace=True)
            self.data.sort_index(inplace=True)

            return self.data

        except Exception as e:
            
            dataFrames = []
            filePaths = [
                self.exchangeFlowsPath,
                self.minerFlowsPath,
                self.flowIndicatorPath,
                self.marketIndicatorPath,
                self.networkIndicatorPath,
                self.marketDataPath,
                self.networkDataPath
            ]

            for filePath in filePaths:
                if not os.path.exists(filePath):
                    raise BacktesterError("feature/data-not-found")
                
                try:
                    df = pd.read_csv(filePath)

                    if "datetime" not in df.columns:
                        raise BacktesterError("feature/missing-columns", details="[BUG] the `datetime` column does not exist in the data file.")
                    
                    df["datetime"] = pd.to_datetime(df["datetime"])
                    df.set_index("datetime", inplace=True)
                    df.sort_index(inplace=True)

                    dataFrames.append(df)
                except Exception as e:
                    raise BacktesterError("feature/fail-to-load-data", details={e})

            if dataFrames:
                mergedData = pd.concat(dataFrames, sort=True, axis=1)

                # Save data
                os.makedirs(self.rawDataPath, exist_ok=True)
                outputPath = f"{self.rawDataPath}/cryptoquant_full_data.csv"

                self.data = mergedData  # Slice the data
                self.data.to_csv(outputPath)

                print("Feature Loader is ready.")

                return self.data
        
            else:
                raise BacktesterError("feature/data-not-found")


