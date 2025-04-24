from fastapi import APIRouter, Depends

from api.v1.routes.deps import getBacktesterService
from services.backtester import BacktesterService
from errors.base_exception import BacktesterError
from schemas.base import ResponseModel
from schemas.backtest import BacktestRequestModel, BacktestResponseModel

backtestRouter = APIRouter(prefix="/backtest", tags=["Backtester"])

@backtestRouter.post("/simulate-trade", response_model=ResponseModel[BacktestResponseModel])
async def simulateTrade(request: BacktestRequestModel, backtestService: BacktesterService = Depends(getBacktesterService)):

    result: BacktestResponseModel = await backtestService.run(request)

    return ResponseModel(
        success=True,
        data = BacktestResponseModel(),
        error = None
    )