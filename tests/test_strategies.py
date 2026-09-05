from __future__ import annotations

import numpy as np
import pandas as pd

from quantlab.strategies.buy_hold import BuyHoldStrategy
from quantlab.strategies.rsi_strategy import RsiStrategy
from quantlab.strategies.sma_cross import SmaCrossStrategy


def make_feature_frame() -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=60, freq="D")
    closes = np.linspace(100.0, 160.0, 60)
    return pd.DataFrame({"Date": dates, "Symbol": "TEST", "Close": closes})


def test_buy_hold_strategy_generates_initial_buy_signal():
    df = make_feature_frame()
    strategy = BuyHoldStrategy()
    signals = strategy.generate_signals(df)
    assert signals.iloc[0] == 1
    assert signals.iloc[-1] == 0


def test_sma_cross_strategy_returns_signal_series():
    df = make_feature_frame()
    strategy = SmaCrossStrategy()
    signals = strategy.generate_signals(df)
    assert isinstance(signals, pd.Series)
    assert set(signals.unique()).issubset({-1, 0, 1})


def test_rsi_strategy_returns_signal_series():
    df = make_feature_frame()
    strategy = RsiStrategy()
    signals = strategy.generate_signals(df)
    assert isinstance(signals, pd.Series)
    assert set(signals.unique()).issubset({-1, 0, 1})
