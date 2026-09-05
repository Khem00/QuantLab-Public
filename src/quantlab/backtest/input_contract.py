from __future__ import annotations

import numpy as np
import pandas as pd


MARKET_DATA_COLUMNS = ("Date", "Symbol", "Close")
SIGNAL_COLUMNS = ("Date", "Symbol", "Signal")
VALID_SIGNALS = frozenset({-1, 0, 1})


def validate_backtest_input(
    data: pd.DataFrame,
    signals: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Validate market data and signals before backtesting.

    The backtest consumes only Date, Symbol, and Close from market data.
    Full canonical OHLCV validation belongs to the data validation boundary.
    This boundary adds requirements specific to backtest execution,
    including signal validity and market/signal alignment.
    """
    _validate_market_data(data)
    _validate_signals(signals)
    _validate_alignment(data, signals)

    return data.copy(), signals.copy()


def _validate_market_data(data: pd.DataFrame) -> None:
    if not isinstance(data, pd.DataFrame):
        raise TypeError(
            "Backtest market data must be a pandas DataFrame"
        )

    if data.empty:
        raise ValueError(
            "Backtest market data must not be empty"
        )

    _require_columns(
        data,
        MARKET_DATA_COLUMNS,
        "Backtest market data",
    )

    if data["Date"].isna().any():
        raise ValueError(
            "Backtest market data Date column contains missing values"
        )

    if not pd.api.types.is_datetime64_any_dtype(data["Date"]):
        raise TypeError(
            "Backtest market data Date column must be datetime"
        )

    _validate_symbols(
        data["Symbol"],
        "Backtest market data",
    )

    if not pd.api.types.is_numeric_dtype(data["Close"]):
        raise TypeError(
            "Backtest market data Close column must be numeric"
        )

    close = data["Close"].astype(float)

    if not np.isfinite(close.to_numpy()).all():
        raise ValueError(
            "Backtest market data Close column must contain only finite values"
        )

    if (close <= 0).any():
        raise ValueError(
            "Backtest market data Close column must contain only positive values"
        )

    if not data["Date"].is_monotonic_increasing:
        raise ValueError(
            "Backtest market data Date column must be sorted ascending"
        )

    if data.duplicated(["Date", "Symbol"]).any():
        raise ValueError(
            "Backtest market data must not contain duplicate Date and Symbol pairs"
        )


def _validate_signals(signals: pd.DataFrame) -> None:
    if not isinstance(signals, pd.DataFrame):
        raise TypeError(
            "Backtest signals must be a pandas DataFrame"
        )

    if signals.empty:
        raise ValueError(
            "Backtest signals must not be empty"
        )

    _require_columns(
        signals,
        SIGNAL_COLUMNS,
        "Backtest signals",
    )

    if signals["Date"].isna().any():
        raise ValueError(
            "Backtest signals Date column contains missing values"
        )

    if not pd.api.types.is_datetime64_any_dtype(signals["Date"]):
        raise TypeError(
            "Backtest signals Date column must be datetime"
        )

    _validate_symbols(
        signals["Symbol"],
        "Backtest signals",
    )

    if not pd.api.types.is_numeric_dtype(signals["Signal"]):
        raise TypeError(
            "Backtest signals Signal column must be numeric"
        )

    signal_values = signals["Signal"].astype(float)

    if not np.isfinite(signal_values.to_numpy()).all():
        raise ValueError(
            "Backtest signals must contain only finite values"
        )

    if not signal_values.isin(VALID_SIGNALS).all():
        raise ValueError(
            "Backtest signals must contain only -1, 0, or 1"
        )

    if not signals["Date"].is_monotonic_increasing:
        raise ValueError(
            "Backtest signals Date column must be sorted ascending"
        )

    if signals.duplicated(["Date", "Symbol"]).any():
        raise ValueError(
            "Backtest signals must not contain duplicate Date and Symbol pairs"
        )


def _validate_alignment(
    data: pd.DataFrame,
    signals: pd.DataFrame,
) -> None:
    market_keys = pd.MultiIndex.from_frame(
        data[["Date", "Symbol"]]
    )
    signal_keys = pd.MultiIndex.from_frame(
        signals[["Date", "Symbol"]]
    )

    unknown_keys = signal_keys.difference(market_keys)

    if len(unknown_keys) > 0:
        raise ValueError(
            "Backtest signals contain Date and Symbol pairs not present in market data"
        )


def _require_columns(
    df: pd.DataFrame,
    required_columns: tuple[str, ...],
    label: str,
) -> None:
    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"{label} is missing required columns: {missing}"
        )


def _validate_symbols(
    symbols: pd.Series,
    label: str,
) -> None:
    if symbols.isna().any():
        raise ValueError(
            f"{label} Symbol column contains missing values"
        )

    if (symbols.astype(str).str.strip() == "").any():
        raise ValueError(
            f"{label} Symbol column contains empty values"
        )
