from __future__ import annotations

import pandas as pd
import pytest

from quantlab.validation.chronological import chronological_split


def make_data(rows: int = 100) -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=rows, freq="D")
    return pd.DataFrame(
        {
            "Date": dates,
            "Symbol": ["BTC-USD"] * rows,
            "Open": range(rows),
            "High": range(rows),
            "Low": range(rows),
            "Close": range(rows),
            "Volume": range(rows),
        }
    )


def test_chronological_split_preserves_time_order():
    data = make_data()

    result = chronological_split(data)

    assert len(result.development) == 70
    assert result.boundary_date == pd.Timestamp("2020-03-11")
    assert result.development["Date"].is_monotonic_increasing
    assert result.holdout["Date"].is_monotonic_increasing


def test_chronological_split_keeps_warmup_context():
    data = make_data()

    result = chronological_split(data, warmup_bars=50)

    assert len(result.holdout) == 80
    assert result.holdout.iloc[0]["Date"] == pd.Timestamp("2020-01-21")
    assert result.holdout.iloc[50]["Date"] == result.boundary_date


def test_chronological_split_does_not_shuffle():
    data = make_data().sample(frac=1.0, random_state=42).reset_index(drop=True)

    result = chronological_split(data)

    assert result.development["Date"].is_monotonic_increasing
    assert result.holdout["Date"].is_monotonic_increasing
    assert result.development.iloc[-1]["Date"] < result.boundary_date


@pytest.mark.parametrize(
    "development_fraction",
    [0, -0.1, 1, 1.1],
)
def test_chronological_split_rejects_invalid_fraction(development_fraction):
    with pytest.raises(ValueError, match="development_fraction"):
        chronological_split(
            make_data(),
            development_fraction=development_fraction,
        )


def test_chronological_split_rejects_negative_warmup():
    with pytest.raises(ValueError, match="warmup_bars"):
        chronological_split(make_data(), warmup_bars=-1)


def test_chronological_split_rejects_empty_data():
    with pytest.raises(ValueError, match="empty"):
        chronological_split(pd.DataFrame())


def test_chronological_split_rejects_missing_date():
    data = make_data().drop(columns=["Date"])

    with pytest.raises(ValueError, match="Date"):
        chronological_split(data)
