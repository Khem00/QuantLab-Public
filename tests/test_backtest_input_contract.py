from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from quantlab.backtest.input_contract import validate_backtest_input


def make_valid_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    dates = pd.date_range("2024-01-01", periods=3, freq="D")

    data = pd.DataFrame(
        {
            "Date": dates,
            "Symbol": ["TEST"] * 3,
            "Close": [100.0, 101.0, 102.0],
        }
    )

    signals = pd.DataFrame(
        {
            "Date": dates,
            "Symbol": ["TEST"] * 3,
            "Signal": [0, 1, -1],
        }
    )

    return data, signals


def test_valid_backtest_inputs_are_accepted():
    data, signals = make_valid_inputs()

    validated_data, validated_signals = validate_backtest_input(data, signals)

    pd.testing.assert_frame_equal(validated_data, data)
    pd.testing.assert_frame_equal(validated_signals, signals)


def test_backtest_contract_returns_independent_copies():
    data, signals = make_valid_inputs()

    validated_data, validated_signals = validate_backtest_input(data, signals)

    validated_data.loc[0, "Close"] = 999.0
    validated_signals.loc[0, "Signal"] = -1

    assert data.loc[0, "Close"] == 100.0
    assert signals.loc[0, "Signal"] == 0


def test_rejects_empty_market_data():
    data, signals = make_valid_inputs()

    with pytest.raises(ValueError, match="market data must not be empty"):
        validate_backtest_input(data.iloc[0:0], signals)


def test_rejects_missing_market_data_columns():
    data, signals = make_valid_inputs()
    data = data.drop(columns=["Close"])

    with pytest.raises(ValueError, match="missing required columns"):
        validate_backtest_input(data, signals)


def test_rejects_invalid_market_data_dates():
    data, signals = make_valid_inputs()
    data["Date"] = data["Date"].dt.strftime("%Y-%m-%d")

    with pytest.raises(TypeError, match="Date column must be datetime"):
        validate_backtest_input(data, signals)


def test_rejects_non_finite_market_prices():
    data, signals = make_valid_inputs()
    data.loc[1, "Close"] = np.inf

    with pytest.raises(ValueError, match="finite"):
        validate_backtest_input(data, signals)


def test_rejects_non_positive_market_prices():
    data, signals = make_valid_inputs()
    data.loc[1, "Close"] = 0.0

    with pytest.raises(ValueError, match="positive"):
        validate_backtest_input(data, signals)


def test_rejects_duplicate_market_keys():
    data, signals = make_valid_inputs()
    data.loc[1, "Date"] = data.loc[0, "Date"]

    with pytest.raises(ValueError, match="duplicate Date and Symbol"):
        validate_backtest_input(data, signals)


def test_rejects_empty_signals():
    data, signals = make_valid_inputs()

    with pytest.raises(ValueError, match="signals must not be empty"):
        validate_backtest_input(data, signals.iloc[0:0])


def test_rejects_invalid_signal_values():
    data, signals = make_valid_inputs()
    signals.loc[1, "Signal"] = 2

    with pytest.raises(ValueError, match="-1, 0, or 1"):
        validate_backtest_input(data, signals)


def test_rejects_duplicate_signal_keys():
    data, signals = make_valid_inputs()
    signals.loc[1, "Date"] = signals.loc[0, "Date"]

    with pytest.raises(ValueError, match="duplicate Date and Symbol"):
        validate_backtest_input(data, signals)


def test_rejects_signal_keys_not_in_market_data():
    data, signals = make_valid_inputs()
    signals.loc[2, "Date"] = pd.Timestamp("2024-01-04")

    with pytest.raises(ValueError, match="not present in market data"):
        validate_backtest_input(data, signals)


def test_rejects_unsorted_market_data():
    data, signals = make_valid_inputs()
    data = data.iloc[[1, 0, 2]].reset_index(drop=True)

    with pytest.raises(ValueError, match="market data Date column must be sorted"):
        validate_backtest_input(data, signals)


def test_rejects_unsorted_signals():
    data, signals = make_valid_inputs()
    signals = signals.iloc[[1, 0, 2]].reset_index(drop=True)

    with pytest.raises(ValueError, match="signals Date column must be sorted"):
        validate_backtest_input(data, signals)
