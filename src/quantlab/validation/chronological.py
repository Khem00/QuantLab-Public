from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ChronologicalSplit:
    development: pd.DataFrame
    holdout: pd.DataFrame
    boundary_date: pd.Timestamp
    development_fraction: float
    holdout_fraction: float
    warmup_bars: int


def chronological_split(
    data: pd.DataFrame,
    *,
    development_fraction: float = 0.70,
    warmup_bars: int = 50,
) -> ChronologicalSplit:
    """Split time-series market data chronologically without shuffling.

    The development portion is the first `development_fraction` of rows.
    The holdout portion begins immediately afterward.

    `warmup_bars` rows immediately preceding the holdout boundary are retained
    in the holdout input so rolling indicators can be computed without using
    future observations. Portfolio evaluation must still begin at the actual
    holdout boundary.
    """
    if data.empty:
        raise ValueError("Cannot split an empty dataset.")

    if not 0 < development_fraction < 1:
        raise ValueError("development_fraction must be between 0 and 1.")

    if warmup_bars < 0:
        raise ValueError("warmup_bars must be non-negative.")

    if "Date" not in data.columns:
        raise ValueError("Dataset must contain a Date column.")

    ordered = data.sort_values("Date").reset_index(drop=True).copy()

    split_index = int(len(ordered) * development_fraction)

    if split_index <= 0 or split_index >= len(ordered):
        raise ValueError("Split must leave observations in both partitions.")

    development = ordered.iloc[:split_index].copy()

    boundary_date = pd.Timestamp(ordered.iloc[split_index]["Date"])

    warmup_start = max(0, split_index - warmup_bars)
    holdout = ordered.iloc[warmup_start:].copy()

    return ChronologicalSplit(
        development=development,
        holdout=holdout,
        boundary_date=boundary_date,
        development_fraction=development_fraction,
        holdout_fraction=1.0 - development_fraction,
        warmup_bars=min(warmup_bars, split_index),
    )
