import uvicorn as uv
from fastapi import FastAPI

from backend.src.errors.base_exception import BacktesterError
from backend.src.handlers.exception_handler import appExceptionHandler




def createApp() -> FastAPI:

    app = FastAPI()

    app.add_exception_handler(BacktesterError, appExceptionHandler)

    return app

app = createApp()

if __name__ == "__main__":
    uv.run(
        "main:app",
        reload=True
    )