import uvicorn as uv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pipeline.feature_loader import FeatureLoader
from configs.path import PathConfig
from data.data_loader import DataLoader
from errors.base_exception import BacktesterError
from handlers.exception_handler import appExceptionHandler
from api.v1.routes import backtestRouter

def createApp() -> FastAPI:

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    app.include_router(router=backtestRouter, prefix="/api/v1")

    app.add_exception_handler(BacktesterError, appExceptionHandler)

    return app

app = createApp()

if __name__ == "__main__":
    # uv.run(
    #     "main:app",
    #     reload=True
    # )

    # PathConfig.createDirectories(PathConfig)
    dataLoader = DataLoader()
    # dataLoader.run(category="exchange-flows")
    # dataLoader.run(category="flow-indicator")
    # dataLoader.run(category="market-indicator")
    # dataLoader.run(category="network-indicator")
    # dataLoader.run(category="miner-flows")
    # dataLoader.run(category="market-data")
    # dataLoader.run(category="network-data")


    featureLoader = FeatureLoader("2023-12-31")
    
    print("Done.")