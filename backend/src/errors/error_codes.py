from typing import Dict

ERROR_REGISTRY: Dict[str, Dict] = {
    "internal/server-error": {
        "message": "An unexpected error occurred",
        "statusCode": 500
    },
    "auth/unauthorized": {
        "message": "Unauthorized access.",
        "statusCode": 401
    },
    "backtest/end-date-before-start-date": {
        "message": "Invalid date interval. The end date must before the start date.",
        "statusCode": 400
    },
    "backtest/invalid-runtime-mode": {
        "message": "Invalid runtime mode. The system currently supports 'backtest' mode only.",
        "statusCode": 400
    },
    "backtest/invalid-entry-exit-logic": {
        "message": "Invalid entry exit logic. The supported entry exit logics are 'mean-reversion', 'trend-following' and 'stoploss-takeprofit' only.",
        "statusCode": 400
    },
    "backtest/invalid-position-sizing-model": {
        "message": "Invalid position sizing model. The supported position sizing models are 'fixed' or 'auto' only.",
        "statusCode": 400
    },
    "backtest/invalid-range": {
        "message": "The valid range is between 0 to 1.",
        "statusCode": 400,
    },
    "data/missing-api-key": {
        "message": "Failed to fetch crypto data. Please provide a valid API key.",
        "statusCode": 401
    },
    "data/fail-to-fetch-data": {
        "message": "Failed to fetch crypto data. Please check the error details.",
        "statusCode": 400
    },
    "data/invalid-provider": {
        "message": "Invalid provider. The supported providers are 'cryptoquant', 'glassnode' or 'coinbase' only.",
        "statusCode": 400
    },
    "data/invalid-endpoint": {
        "message": "Invalid endpoint. Please check the documentation.",
        "statusCode": 400
    }
}