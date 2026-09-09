from __future__ import annotations

import pandas as pd

from quantlab.data.trust import DataTrustAssessment, DataTrustState
from quantlab.validation.backtest import run_holdout_backtest


def make_data(rows: int = 100) -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=rows, freq="D")

    return pd.DataFrame(
        {
            "Date": dates,
            "Symbol": ["BTC-USD"] * rows,
            "Close": [100.0] * rows,
        }
    )


def make_trust() -> DataTrustAssessment:
    return DataTrustAssessment(
        state=DataTrustState.TRUSTED,
        capability="backtest",
        suitable=True,
    )


def test_holdout_equity_curve_starts_at_oos_boundary():
    data = make_data()
    signals = pd.Series(1, index=data.index, dtype=int)
    boundary = pd.Timestamp("2020-03-11")

    result = run_holdout_backtest(
        data,
        signals,
        boundary_date=boundary,
        trust_assessment=make_trust(),
        initial_capital=100000.0,
        warmup_bars=50,
    )

    assert result.evaluation_start == boundary
    assert result.evaluation_equity_curve.index[0] == boundary
    assert len(result.evaluation_equity_curve) == 30


def test_holdout_portfolio_is_fresh_at_oos_boundary():
    data = make_data()
    signals = pd.Series(1, index=data.index, dtype=int)
    boundary = pd.Timestamp("2020-03-11")

    result = run_holdout_backtest(
        data,
        signals,
        boundary_date=boundary,
        trust_assessment=make_trust(),
        initial_capital=100000.0,
        warmup_bars=50,
    )

    first_value = result.evaluation_equity_curve.iloc[0]

    assert first_value == 100000.0


def test_holdout_trade_cannot_occur_during_warmup():
    data = make_data()
    signals = pd.Series(1, index=data.index, dtype=int)
    boundary = pd.Timestamp("2020-03-11")

    result = run_holdout_backtest(
        data,
        signals,
        boundary_date=boundary,
        trust_assessment=make_trust(),
        initial_capital=100000.0,
        warmup_bars=50,
    )

    trades = result.backtest.trade_log.trades

    assert trades
    assert all(
        pd.Timestamp(trade.timestamp) >= boundary
        for trade in trades
    )
