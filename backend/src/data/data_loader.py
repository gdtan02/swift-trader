import os
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Any

from configs.path import PathConfig
from errors.base_exception import BacktesterError
from data.api_client import APIClient
from data.endpoints.endpoints import endpointsParams
from utils.util import convertDatetimeToUnixTimestamp, getStartTime

class DataLoader:
    """Responsible for fetching data from API providers and store into CSV format"""

    def __init__(self, apiKey: Optional[str] = None, provider: Optional[str] = "cryptoquant"):

        if provider is not None and provider not in endpointsParams:
            raise BacktesterError("data/invalid-provider")

        self.apiClient = APIClient(apiKey=apiKey, provider=provider)
        self.endpoints = endpointsParams[provider]
        self.dataframes: List[pd.DataFrame] = []
        self.df: pd.DataFrame = pd.DataFrame()
        self.limit = 50000

    def run(self, category: str) -> None:
        
        startTime = getStartTime(dayInterval=10*365)   # Default 10 years
        startTime = convertDatetimeToUnixTimestamp(startTime)
        
        if category not in self.endpoints:
            raise BacktesterError("data/invalid-category")

        for endpoint, params in self.endpoints[category].items():
            endpointUrl = self._parseEndpointUrl(category, startTime, endpoint, params)
            response = self.apiClient.get(endpointUrl)["data"]

            if response is None or []:
                raise BacktesterError("data/fail-to-fetch-data", details="Response data is empty.")

            # Preprocess data
            data = pd.DataFrame(response).drop(columns="start_time")

            # Replace 'date' with 'datetime'
            if self.endpoints[category][endpoint]["window"] == "day":
                data.rename(columns={"date": "datetime"}, inplace=True)
                                
            data["datetime"] = pd.to_datetime(data["datetime"])
            data.set_index("datetime", inplace=True)

            # Add suffix for these two categories to avoid duplicated column names
            if category == "miner-flows":
                columnNames = data.columns
                columnNames = { name: f"miner_{name}" for name in columnNames }
                data.rename(columns=columnNames, inplace=True)

            elif category == "exchange-flows":
                columnNames = data.columns
                columnNames = { name: f"exchange_{name}" for name in columnNames }
                data.rename(columns=columnNames, inplace=True)

            self.dataframes.append(data)

        self.df = pd.concat(self.dataframes, sort=True, axis=1)
        self.df.sort_index(inplace=True)

        # Clean data
        self.df.drop_duplicates(inplace=True)
        self.df.interpolate(method="linear", limit_direction="forward", inplace=True)

        self.saveData(data=self.df, category=category, provider = self.apiClient.provider)

    def saveData(self, data: pd.DataFrame, category: str, provider: str):
        os.makedirs(PathConfig.RAW_DATA_DIR, exist_ok=True)

        # Rename category
        category = category.replace("-", "_")
        outputPath = f"{PathConfig.RAW_DATA_DIR}/{provider}_{category}.csv"
        data.to_csv(outputPath)

    def _parseEndpointUrl(self, category: str, startTime: int, endpoint: str, params: Dict[str, str]) -> str:
        endpointUrl = f"btc/{category}/{endpoint}?start_time={startTime}&limit={self.limit}"

        for key, value in params.items():
            endpointUrl += f"&{key}={value}"

        return endpointUrl

