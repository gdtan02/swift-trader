from fastapi import APIRouter, Depends

from errors.base_exception import BacktesterError
from schemas.base import ResponseModel
from schemas.backtest import BacktestRequestModel, BacktestResponseModel

backtestRouter = APIRouter(prefix="/backtest", tags=["Backtester"])

@backtestRouter.post("/simulate-trade", response_model=ResponseModel[BacktestResponseModel])
async def simulateTrade(request: BacktestRequestModel):

    if request:
        print("Test.")

    return ResponseModel(
        success=True,
        data = BacktestResponseModel()
    )