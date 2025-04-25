from typing import Annotated
import uvicorn as uv
from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from schemas.backtest import BacktestRequestModel, BacktestResponseModel
from schemas.base import ResponseModel
from services.backtester import BacktesterService
# from strategies.xgb_strategy import XGBoostStrategy
from pipeline.feature_loader import FeatureLoader
from configs.path import PathConfig
from data.data_loader import DataLoader
from errors.base_exception import BacktesterError
from handlers.exception_handler import appExceptionHandler
from api.v1.routes import backtestRouter

_backtesterService = BacktesterService()

def getBacktesterService() -> BacktesterService:
    global _backtesterService
    if _backtesterService is None:
        _backtesterService = BacktesterService()
    return _backtesterService

BacktesterDependency = Annotated[BacktesterService, Depends(getBacktesterService)]


backtestRouter = APIRouter(prefix="/backtest", tags=["Backtester"])

@backtestRouter.post("/simulate-trade", response_model=ResponseModel[BacktestResponseModel])
async def simulateTrade(request: BacktestRequestModel, backtestService: BacktesterService = Depends(getBacktesterService)):

    result: BacktestResponseModel = await backtestService.run(request)

    return ResponseModel(
        success=True,
        data = result,
        error = None
    )

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(backtestRouter, prefix="/api/v1")
app.add_exception_handler(BacktesterError, appExceptionHandler)

if __name__ == "__main__":
    uv.run(
        "main:app",
        reload=True
    )