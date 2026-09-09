from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class HoldoutInput:
    data: pd.DataFrame
    signals: pd.Series
    evaluation_start: pd.Timestamp


def prepare_holdout_input(
    data: pd.DataFrame,
    signals: pd.Series,
    *,
    boundary_date: pd.Timestamp,
    warmup_bars: int = 50,
) -> HoldoutInput:
    """Prepare chronological OOS input while preventing pre-OOS positions.

    Historical rows preceding the holdout boundary are retained only as
    indicator warm-up context. Their signals are replaced with neutral signals
    so the fresh OOS portfolio cannot enter a position before evaluation begins.
    """
    if data.empty:
        raise ValueError("Cannot prepare holdout input from empty data.")

    if len(data) != len(signals):
        raise ValueError("Data and signals must have the same length.")

    if warmup_bars < 0:
        raise ValueError("warmup_bars must be non-negative.")

    if "Date" not in data.columns:
        raise ValueError("Dataset must contain a Date column.")

    dates = pd.to_datetime(data["Date"])
    boundary_date = pd.Timestamp(boundary_date)

    boundary_positions = dates[dates >= boundary_date]

    if boundary_positions.empty:
        raise ValueError("boundary_date is not present in the dataset.")

    boundary_position = boundary_positions.index[0]

    warmup_start = max(0, boundary_position - warmup_bars)

    holdout_data = data.iloc[warmup_start:].copy()
    holdout_signals = signals.iloc[warmup_start:].copy()

    pre_boundary = pd.to_datetime(holdout_data["Date"]) < boundary_date
    holdout_signals.loc[pre_boundary] = 0

    return HoldoutInput(
        data=holdout_data.reset_index(drop=True),
        signals=holdout_signals.reset_index(drop=True),
        evaluation_start=boundary_date,
    )
