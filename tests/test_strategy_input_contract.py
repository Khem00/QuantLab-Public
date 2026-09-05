from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from quantlab.strategies.input_contract import validate_strategy_input


def make_valid_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=3, freq="D"),
            "Symbol": ["TEST", "TEST", "TEST"],
            "Open": [99.0, 100.0, 101.0],
            "High": [101.0, 102.0, 103.0],
            "Low": [98.0, 99.0, 100.0],
            "Close": [100.0, 101.0, 102.0],
            "Volume": [1000, 1100, 1200],
        }
    )


def test_valid_strategy_input_is_accepted():
    df = make_valid_frame()

    result = validate_strategy_input(df)

    pd.testing.assert_frame_equal(result, df)


def test_strategy_input_does_not_require_unused_ohlcv_columns():
    df = make_valid_frame()[["Date", "Symbol", "Close"]]

    result = validate_strategy_input(df)

    pd.testing.assert_frame_equal(result, df)


def test_rejects_empty_dataset():
    df = make_valid_frame().iloc[0:0]

    with pytest.raises(ValueError, match="must not be empty"):
        validate_strategy_input(df)


def test_rejects_missing_required_columns():
    df = make_valid_frame().drop(columns=["Close"])

    with pytest.raises(ValueError, match="missing required columns"):
        validate_strategy_input(df)


def test_rejects_non_datetime_dates():
    df = make_valid_frame()
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    with pytest.raises(TypeError, match="Date column must be datetime"):
        validate_strategy_input(df)


def test_rejects_missing_symbols():
    df = make_valid_frame()
    df.loc[1, "Symbol"] = None

    with pytest.raises(ValueError, match="Symbol column contains missing"):
        validate_strategy_input(df)


def test_rejects_non_numeric_close():
    df = make_valid_frame()
    df["Close"] = ["100", "101", "102"]

    with pytest.raises(TypeError, match="Close column must be numeric"):
        validate_strategy_input(df)


def test_rejects_non_finite_close():
    df = make_valid_frame()
    df.loc[1, "Close"] = np.inf

    with pytest.raises(ValueError, match="only finite values"):
        validate_strategy_input(df)


def test_rejects_non_positive_close():
    df = make_valid_frame()
    df.loc[1, "Close"] = 0.0

    with pytest.raises(ValueError, match="only positive values"):
        validate_strategy_input(df)


def test_rejects_unsorted_dates():
    df = make_valid_frame()
    df = df.iloc[[1, 0, 2]].reset_index(drop=True)

    with pytest.raises(ValueError, match="sorted ascending"):
        validate_strategy_input(df)


def test_contract_does_not_mutate_input():
    df = make_valid_frame()
    original = df.copy()

    result = validate_strategy_input(df)

    result.loc[0, "Close"] = 999.0

    pd.testing.assert_frame_equal(df, original)
