from pydantic import BaseModel
from typing import Dict, List, Optional, Any

from errors.base_exception import BacktesterError
from schemas.order import Order, OrderSide

class Position(BaseModel):
    asset: str
    quantity: float = 0.0
    avgEntryPrice: float = 0.0
    currentPrice: float = 0.0
    unrealizedPnl: float = 0.0
    realizedPnl: float = 0.0

    @property
    def totalValue(self) -> float:
        """Current position value"""
        return self.quantity * self.currentPrice
    
    def updateUnrealizedPnl(self) -> float:
        """Unrealized profit and loss based on current price"""
        if self.quantity <= 0:
            self.unrealizedPnl = 0.0
        else:
            self.unrealizedPnl = (self.currentPrice - self.avgEntryPrice) * self.quantity
        return self.unrealizedPnl
    
    def updatePosition(self, order: Order) -> None:
        """Update the position based on an executed order."""
        if order.asset != self.asset:
            return
        
        # Update average entry price and quantity
        if order.orderSide == OrderSide.BUY:
            totalCost = (self.avgEntryPrice * self.quantity) + order.value
            newQuantity = self.quantity + order.quantity

            # Update position
            self.quantity = newQuantity
            self.avgEntryPrice = totalCost / newQuantity if newQuantity > 0 else 0.0

        elif order.orderSide == OrderSide.SELL:

            if order.quantity > self.quantity:
                raise BacktesterError("trade/insufficient-quantity")
            
            if self.quantity > 0:
                tradePnl = (order.executionPrice * self.avgEntryPrice) * order.quantity
                self.realizedPnl += tradePnl

            newQuantity = self.quantity - order.quantity

            if newQuantity <= 0:
                self.avgEntryPrice = 0.0

            self.quantity = max(0, newQuantity)

        self.updateUnrealizedPnl()
            

