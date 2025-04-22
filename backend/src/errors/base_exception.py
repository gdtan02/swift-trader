from fastapi import status

from backend.src.errors.error_codes import ERROR_REGISTRY

class BacktesterError(Exception):

    def __init__(self, code: str, details: str = None):

        if code not in ERROR_REGISTRY:
            # Fallback to internal error
            code = "internal/server-error"

        errors = ERROR_REGISTRY[code]
        self.code = code
        self.message = errors["message"]
        self.statusCode = errors.get("statusCode", status.HTTP_400_BAD_REQUEST)
        self.details = details