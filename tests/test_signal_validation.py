from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from quantlab.signals.validation import validate_signal_series


def make_index() -> pd.Index:
    return pd.RangeIndex(start=0, stop=4)


def test_valid_signals_are_accepted_and_normalized():
    signals = pd.Series([0, 1, -1, 0], index=make_index())

    result = validate_signal_series(signals, make_index())

    assert result.dtype == int
    assert result.tolist() == [0, 1, -1, 0]


def test_rejects_non_series_output():
    with pytest.raises(TypeError, match="pandas Series"):
        validate_signal_series([0, 1, -1, 0], make_index())


def test_rejects_misaligned_index():
    signals = pd.Series([0, 1, -1, 0], index=pd.RangeIndex(1, 5))

    with pytest.raises(ValueError, match="same index"):
        validate_signal_series(signals, make_index())


def test_rejects_non_numeric_signals():
    signals = pd.Series(["hold", "buy", "sell", "hold"], index=make_index())

    with pytest.raises(TypeError, match="numeric"):
        validate_signal_series(signals, make_index())


def test_rejects_nan_signals():
    signals = pd.Series([0, 1, np.nan, 0], index=make_index())

    with pytest.raises(ValueError, match="finite"):
        validate_signal_series(signals, make_index())


def test_rejects_infinite_signals():
    signals = pd.Series([0, 1, np.inf, 0], index=make_index())

    with pytest.raises(ValueError, match="finite"):
        validate_signal_series(signals, make_index())


def test_rejects_unknown_signal_values():
    signals = pd.Series([0, 1, 2, 0], index=make_index())

    with pytest.raises(ValueError, match="-1, 0, or 1"):
        validate_signal_series(signals, make_index())
