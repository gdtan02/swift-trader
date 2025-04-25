from fastapi.responses import JSONResponse
from fastapi import Request
from errors import BacktesterError

async def appExceptionHandler(request: Request, exc: BacktesterError):
    
  return JSONResponse(
        status_code= exc.statusCode,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )