from pydantic_settings import BaseSettings


class BacktestDefaultConfig(BaseSettings):
    mode: RuntimeMode.BACKTEST
    