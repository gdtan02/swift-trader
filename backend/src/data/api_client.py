import os
import requests
from typing import Optional
from dotenv import load_dotenv

from errors.base_exception import BacktesterError

load_dotenv()

class APIClient:

    def __init__(self, provider: Optional[str], apiKey: Optional[str]):
        self.apiKey = os.getenv("CYBOTRADE_API_KEY") or apiKey
        self.baseUrl = os.getenv("CYBOTRADE_BASE_URL") or "https://api.datasource.cybotrade.rs"
        self.provider = provider or "cryptoquant"

    def get(self, endpoint: str):

        if self.apiKey is None:
            raise BacktesterError("data/missing-api-key")

        url = f"{self.baseUrl}/{self.provider}/{endpoint}"
        headers = { "X-API-Key": self.apiKey }

        print("URL:", url)

        try: 
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
    
        except requests.exceptions.HTTPError as httpErr:
            raise BacktesterError("data/fail-to-fetch-data", details=f"HTTP Error occurred: {httpErr}")
        
        except requests.exceptions.ConnectionError as connErr:
            raise BacktesterError("data/fail-to-fetch-data", details=f"Connection Error occurred: {connErr}")
        
        except requests.exceptions.Timeout as timeoutErr:
            raise BacktesterError("data/fail-to-fetch-data", details=f"Connection Timeout: {timeoutErr}")
        
        except requests.exceptions.JSONDecodeError as jsonErr:
            raise BacktesterError("data/fail-to-fetch-data", details=f"Error while decoding JSON: {jsonErr}")
        
        except requests.exceptions.RequestException as err:
            raise BacktesterError("data/fail-to-fetch-data", details=f"Request Error: {err}")
