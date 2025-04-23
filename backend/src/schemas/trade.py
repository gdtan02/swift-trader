from pydantic import BaseModel
from typing import Dict, List, Optional, Tuple, Any

from schemas.position import Position, Positions

class TradePortfolio(BaseModel):
    initialCapital: float = None
    finalEquity: float = None
    equityCurve: Tuple[str, float] = ()
    drawdownCurve: Tuple[str, float] = ()
    positions: Positions = Positions()

