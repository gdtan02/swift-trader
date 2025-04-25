from abc import ABC, abstractmethod

import pandas as pd

class Feature(ABC):
    """Abstract base class for feature."""

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform the data into the features."""
        pass
