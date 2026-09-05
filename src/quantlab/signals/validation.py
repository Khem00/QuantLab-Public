from __future__ import annotations

import numpy as np
import pandas as pd


VALID_SIGNALS = frozenset({-1, 0, 1})


def validate_signal_series(
    signals: pd.Series,
    expected_index: pd.Index,
) -> pd.Series:
    """Validate and normalize a strategy's signal output.

    Signals must:
    - be a pandas Series
    - have the same index as the input dataset
    - contain only finite numeric values
    - contain only -1, 0, or 1
    """
    if not isinstance(signals, pd.Series):
        raise TypeError("Strategy signals must be a pandas Series")

    if not signals.index.equals(expected_index):
        raise ValueError("Strategy signals must use the same index as the dataset")

    if not pd.api.types.is_numeric_dtype(signals):
        raise TypeError("Strategy signals must contain numeric values")

    numeric_signals = signals.astype(float)

    if not np.isfinite(numeric_signals.to_numpy()).all():
        raise ValueError("Strategy signals must contain only finite values")

    if not numeric_signals.isin(VALID_SIGNALS).all():
        raise ValueError("Strategy signals must contain only -1, 0, or 1")

    return numeric_signals.astype(int)
