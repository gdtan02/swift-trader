from typing import Dict

ERROR_REGISTRY: Dict[str, Dict] = {
    "internal/server-error": {
        "message": "An unexpected error occurred",
        "statusCode": 500
    },
    "algorithm/model-not-fitted": {
        "message": "Please run the `fit` method first to train the model.",
        "statusCode": 400
    },
    "auth/unauthorized": {
        "message": "Unauthorized access.",
        "statusCode": 401
    },
    "backtest/invalid-date-interval": {
        "message": "Invalid date interval. Please look at the error details.",
        "statusCode": 400
    },
    "backtest/invalid-runtime-mode": {
        "message": "Invalid runtime mode. The system currently supports 'backtest' mode only.",
        "statusCode": 400
    },
    "backtest/invalid-entry-exit-logic": {
        "message": "Invalid entry exit logic. The supported entry exit logics are 'mean-reversion' and 'trend-following' only.",
        "statusCode": 400
    },
    "backtest/invalid-position-sizing-model": {
        "message": "Invalid position sizing model. The supported position sizing models are 'fixed' or 'auto' only.",
        "statusCode": 400
    },
    "backtest/invalid-position-size": {
        "message": "Invalid position size. The position size should be greater than 0.0 and not greater than 1.0."
    },
    "backtest/invalid-range": {
        "message": "The valid range is between 0 to 1.",
        "statusCode": 400,
    },
    "backtest/date-interval-out-of-range": {
        "message": "The starting date or the ending date is outside of valid date interval range.",
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
    },
    "feature/data-not-found": {
        "message": "The data does not exist. Please run the DataLoader first.",
        "statusCode": 400
    },
    "feature/fail-to-load-data": {
        "message": "Error while reading CSV files.",
        "statusCode": 500
    },
    "feature/missing-columns": {
        "message": "Missing columns required to calculate the features.",
        "statusCode": 400
    },
    "feature/missing-features": {
        "message": "Please provide the features to load.",
        "statusCode": 400
    },
    "strategy/data-not-loaded": {
        "message": "Failed to load the data to run strategy.",
        "statusCode": 400
    },
    "strategy/invalid-threshold": {
        "message": "Invalid threshold value. Please check the details for the valid range.",
        "statusCode": 400
    }
}