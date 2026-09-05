from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from quantlab.features.indicators import ema20, ema50, rsi14, sma20, sma50
from quantlab.features.momentum import momentum_10d, momentum_30d
from quantlab.features.returns import cumulative_returns, daily_returns, log_returns
from quantlab.features.volatility import annualized_volatility, maximum_drawdown, rolling_volatility


def make_sample_frame() -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=60, freq="D")
    closes = np.array([100 + i * 0.5 for i in range(60)], dtype=float)
    return pd.DataFrame({"Date": dates, "Symbol": "TEST", "Close": closes})


def test_returns_features_are_calculated():
    df = make_sample_frame()
    assert daily_returns(df).iloc[1] == pytest.approx(0.005)
    assert log_returns(df).iloc[1] > 0
    assert cumulative_returns(df).iloc[-1] > 0


def test_indicator_features_return_series():
    df = make_sample_frame()
    assert isinstance(sma20(df), pd.Series)
    assert isinstance(sma50(df), pd.Series)
    assert isinstance(ema20(df), pd.Series)
    assert isinstance(ema50(df), pd.Series)
    assert isinstance(rsi14(df), pd.Series)


def test_volatility_and_drawdown_are_numeric():
    df = make_sample_frame()
    assert np.isfinite(rolling_volatility(df).dropna().iloc[-1])
    assert np.isfinite(annualized_volatility(df))
    assert np.isfinite(maximum_drawdown(df))


def test_momentum_features_return_series():
    df = make_sample_frame()
    assert isinstance(momentum_10d(df), pd.Series)
    assert isinstance(momentum_30d(df), pd.Series)
