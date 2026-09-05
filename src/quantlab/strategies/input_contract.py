from __future__ import annotations

import numpy as np
import pandas as pd


STRATEGY_INPUT_COLUMNS = ("Date", "Symbol", "Close")


def validate_strategy_input(df: pd.DataFrame) -> pd.DataFrame:
    """Validate the market-data contract required by strategy consumers.

    Strategies require only Date, Symbol, and Close. Full canonical OHLCV
    validation belongs to the data validation boundary and is intentionally
    not required here.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Strategy input must be a pandas DataFrame")

    if df.empty:
        raise ValueError("Strategy input dataset must not be empty")

    _require_columns(
        df,
        STRATEGY_INPUT_COLUMNS,
        "Strategy input",
    )

    if df["Date"].isna().any():
        raise ValueError(
            "Strategy input Date column contains missing values"
        )

    if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
        raise TypeError(
            "Strategy input Date column must be datetime"
        )

    _validate_symbols(
        df["Symbol"],
        "Strategy input",
    )

    if not pd.api.types.is_numeric_dtype(df["Close"]):
        raise TypeError(
            "Strategy input Close column must be numeric"
        )

    close = df["Close"].astype(float)

    if not np.isfinite(close.to_numpy()).all():
        raise ValueError(
            "Strategy input Close column must contain only finite values"
        )

    if (close <= 0).any():
        raise ValueError(
            "Strategy input Close column must contain only positive values"
        )

    if not df["Date"].is_monotonic_increasing:
        raise ValueError(
            "Strategy input Date column must be sorted ascending"
        )

    return df.copy()


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
