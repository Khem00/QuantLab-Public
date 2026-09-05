from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class BaseStrategy(ABC):
    """Base interface for quantitative strategies."""

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """Return a Series of trading signals for the provided DataFrame."""
        raise NotImplementedError
