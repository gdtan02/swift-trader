from abc import ABC, abstractmethod

class BasePositionSizer(ABC):
    """Base class for position sizing strategies."""

    @abstractmethod
    def calculatePositionSize(self, availableCash: float) -> float:
        """Calculate the position size in cash amount."""
        pass