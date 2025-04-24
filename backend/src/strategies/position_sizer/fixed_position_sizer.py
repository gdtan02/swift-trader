
from errors.base_exception import BacktesterError
from strategies.position_sizer.base_position_sizer import BasePositionSizer

class FixedProportionPositionSizer(BasePositionSizer):

    def __init__(self, proportion: float = 1.0):

        if proportion <= 0 or proportion > 1.0:
            raise BacktesterError("backtest/invalid-position-size")
        
        self.proportion = proportion


    def calculatePositionSize(self, availableCash: float) -> float:
        return availableCash * self.proportion