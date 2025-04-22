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
}