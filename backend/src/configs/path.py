import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class PathConfig:

    BASE_DIR: str = str(Path(__file__).resolve().parent.parent.parent)
    
    DATA_DIR: str = f"{BASE_DIR}/data"
    RAW_DATA_DIR: str = f"{DATA_DIR}/raw"
    FEATURES_DIR: str = f"{DATA_DIR}/features"

    MODELS_DIR: str = f"{BASE_DIR}/models"