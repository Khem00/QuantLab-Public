from __future__ import annotations

import pandas as pd
import pytest

from quantlab.validation.holdout import prepare_holdout_input


def make_data(rows: int = 100) -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=rows, freq="D")

    return pd.DataFrame(
        {
            "Date": dates,
            "Symbol": ["BTC-USD"] * rows,
            "Close": range(100, 100 + rows),
        }
    )


def test_holdout_keeps_warmup_context():
    data = make_data()
    signals = pd.Series(1, index=data.index, dtype=int)
    boundary = pd.Timestamp("2020-03-11")

    result = prepare_holdout_input(
        data,
        signals,
        boundary_date=boundary,
        warmup_bars=50,
    )

    assert len(result.data) == 80
    assert result.data.iloc[0]["Date"] == pd.Timestamp("2020-01-21")
    assert result.evaluation_start == boundary


def test_holdout_neutralizes_warmup_signals():
    data = make_data()
    signals = pd.Series(1, index=data.index, dtype=int)
    boundary = pd.Timestamp("2020-03-11")

    result = prepare_holdout_input(
        data,
        signals,
        boundary_date=boundary,
        warmup_bars=50,
    )

    warmup = result.data["Date"] < boundary
    oos = result.data["Date"] >= boundary

    assert (result.signals[warmup] == 0).all()
    assert (result.signals[oos] == 1).all()


def test_holdout_preserves_oos_signal_values():
    data = make_data()
    signals = pd.Series(
        [0, 1, -1, 1] * 25,
        index=data.index,
        dtype=int,
    )
    boundary = pd.Timestamp("2020-03-11")

    result = prepare_holdout_input(
        data,
        signals,
        boundary_date=boundary,
        warmup_bars=50,
    )

    original_oos = signals[data["Date"] >= boundary].reset_index(drop=True)
    result_oos = result.signals[result.data["Date"] >= boundary].reset_index(drop=True)

    pd.testing.assert_series_equal(
        result_oos,
        original_oos,
        check_names=False,
    )


def test_holdout_does_not_use_development_position():
    data = make_data()
    signals = pd.Series(1, index=data.index, dtype=int)
    boundary = pd.Timestamp("2020-03-11")

    result = prepare_holdout_input(
        data,
        signals,
        boundary_date=boundary,
        warmup_bars=50,
    )

    first_oos_position = result.signals[result.data["Date"] >= boundary].iloc[0]

    assert first_oos_position == 1
    assert (result.signals[result.data["Date"] < boundary] == 0).all()


def test_holdout_rejects_length_mismatch():
    data = make_data()
    signals = pd.Series(1, index=range(99), dtype=int)

    with pytest.raises(ValueError, match="same length"):
        prepare_holdout_input(
            data,
            signals,
            boundary_date=pd.Timestamp("2020-03-11"),
        )


def test_holdout_rejects_missing_boundary():
    data = make_data()
    signals = pd.Series(1, index=data.index, dtype=int)

    with pytest.raises(ValueError, match="boundary_date"):
        prepare_holdout_input(
            data,
            signals,
            boundary_date=pd.Timestamp("2025-01-01"),
        )


def test_holdout_rejects_negative_warmup():
    data = make_data()
    signals = pd.Series(1, index=data.index, dtype=int)

    with pytest.raises(ValueError, match="warmup_bars"):
        prepare_holdout_input(
            data,
            signals,
            boundary_date=pd.Timestamp("2020-03-11"),
            warmup_bars=-1,
        )
