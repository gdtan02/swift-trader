import os
from dotenv import load_dotenv
from pathlib import Path
from pydantic_settings import BaseSettings

load_dotenv()

class PathSettings(BaseSettings):

    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    
    DATA_DIR =  BASE_DIR / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    FEATURES_DIR = DATA_DIR / "features"

    MODELS_DIR = BASE_DIR / "models"

    class Config:
        env_file = ".env"
        case_sensitive = True