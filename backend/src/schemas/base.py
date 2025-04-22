from pydantic import BaseModel
from typing import Optional, Generic, TypeVar

T = TypeVar("T")

class ErrorDetails(BaseModel):
    """Base error details"""
    code: str
    message: str
    details: Optional[str] = None

class ResponseModel(BaseModel, Generic[T]):
    """Base response model for all API endpoints"""
    success: bool
    data: Optional[T] = None
    error: Optional[ErrorDetails] = None

