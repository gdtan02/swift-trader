from fastapi import APIRouter, Depends

from errors.base_exception import BacktesterError
from schemas.base import ResponseModel
from schemas.backtest import BacktestRequestModel, BacktestResponseModel

router = APIRouter(prefix="/backtest", tags=["Backtester"])

@router.post("/simulate-trade", response_model=ResponseModel[BacktestResponseModel])
async def simulateTrade(request: BacktestRequestModel):

    if request:
        print("Test.")

    return ResponseModel(
        success=True,
        data = BacktestResponseModel()
    )