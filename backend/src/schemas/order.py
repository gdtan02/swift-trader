from pydantic import BaseModel, field_validator
from typing import Union, List, Dict, Any, Optional
from datetime import date, datetime
from enum import Enum
from uuid import UUID, uuid4

from errors.base_exception import BacktesterError

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop-limit"
    TAKE_PROFIT = "take-profit"

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class Order(BaseModel):
    id: UUID = uuid4()
    timestamp: Union[date, datetime]
    asset: str
    orderType: OrderType
    orderSide: OrderSide
    status: OrderStatus = "pending"
    quantity: float
    price: Optional[float] = None
    executionPrice: Optional[float] = None
    executionTimestamp: Optional[datetime] = None
    commissionFee: float = 0.0
    cancelReason: Optional[str] = None
    pnl: Optional[float] = None

    @property
    def value(self) -> float:
        if self.executionPrice is not None:
            return self.quantity * self.executionPrice
        elif self.price is not None:
            return self.quantity * self.price
        else:
            return 0.0
        
    @field_validator("price", "executionPrice")
    def validatePrices(cls, v) -> float:
        """Validate prices are positive"""
        if v is not None and v <= 0:
            raise BacktesterError("trade/invalid-order-price")
        return v
    
    @field_validator("quantity")
    def validateQuantity(cls, v) -> float:
        """ Validate that quantity must be positive"""
        if v <= 0:
            raise BacktesterError("trade/invalid-order-quantity")
        return v
    
    def calculatePnl(self, referencePrice: float) -> float:
        """
        Calculate profit/loss for the order based on a reference price.
        For BUY orders, P&L is calculated against current market price.
        For SELL orders, P&L is calculated against the average entry price.
        """
        if self.status != OrderStatus.COMPLETED or not self.executionPrice:
            return 0.0
        
        if self.orderSide == OrderSide.BUY:
            # P&L is unrealized: Current price VS execution price
            pnl = (referencePrice - self.executionPrice) * self.quantity
        elif self.orderSide == OrderSide.SELL:
            # P&L is realized: execution price vs average entry price
            pnl = (self.executionPrice - referencePrice) * self.quantity

        self.pnl = pnl - self.commissionFee
        return self.pnl
        