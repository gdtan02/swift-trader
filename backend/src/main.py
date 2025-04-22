import uvicorn as uv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from errors.base_exception import BacktesterError
from handlers.exception_handler import appExceptionHandler
from api.v1.routes import router

def createApp() -> FastAPI:

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    app.include_router(router=router, prefix="/api/v1")

    app.add_exception_handler(BacktesterError, appExceptionHandler)

    return app

app = createApp()

if __name__ == "__main__":
    uv.run(
        "main:app",
        reload=True
    )