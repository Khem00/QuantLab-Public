from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from quantlab.backtest.engine import BacktestEngine
from quantlab.backtest.result import BacktestResult
from quantlab.signals.validation import validate_signal_series
from quantlab.validation.holdout import prepare_holdout_input


@dataclass(frozen=True)
class HoldoutBacktestResult:
    backtest: BacktestResult
    evaluation_equity_curve: pd.Series
    evaluation_start: pd.Timestamp


def run_holdout_backtest(
    data: pd.DataFrame,
    signals: pd.Series,
    *,
    boundary_date: pd.Timestamp,
    trust_assessment,
    initial_capital: float = 100000.0,
    commission: float = 0.0,
    slippage: float = 0.0,
    position_size: float = 1.0,
    warmup_bars: int = 50,
) -> HoldoutBacktestResult:
    """Run a fresh chronological holdout backtest.

    Warm-up rows are processed only to provide indicator context. Their
    signals are neutralized, preventing a pre-OOS position. The returned
    evaluation equity curve begins at the true OOS boundary.
    """
    holdout = prepare_holdout_input(
        data,
        signals,
        boundary_date=boundary_date,
        warmup_bars=warmup_bars,
    )

    signal_frame = pd.DataFrame(
        {
            "Date": holdout.data["Date"],
            "Symbol": holdout.data["Symbol"],
            "Signal": holdout.signals,
        }
    )

    signal_frame["Date"] = pd.to_datetime(signal_frame["Date"])
    signal_frame = signal_frame.reset_index(drop=True)

    validate_signal_series(
        holdout.signals,
        expected_index=holdout.data.index,
    )

    engine = BacktestEngine(
        initial_capital=initial_capital,
        commission=commission,
        slippage=slippage,
        position_size=position_size,
    )

    backtest = engine.run(
        holdout.data,
        signal_frame,
        trust_assessment=trust_assessment,
    )

    evaluation_mask = holdout.data["Date"] >= holdout.evaluation_start

    evaluation_equity_curve = pd.Series(
        backtest.equity_curve.loc[evaluation_mask.to_numpy()].to_numpy(),
        index=pd.to_datetime(
            holdout.data.loc[evaluation_mask, "Date"]
        ),
        dtype=float,
        name="Portfolio_Value",
    )

    if evaluation_equity_curve.empty:
        raise ValueError("Holdout evaluation period produced no observations.")

    return HoldoutBacktestResult(
        backtest=backtest,
        evaluation_equity_curve=evaluation_equity_curve,
        evaluation_start=holdout.evaluation_start,
    )
