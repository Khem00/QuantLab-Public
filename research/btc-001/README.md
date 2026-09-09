# BTC #001 — SMA20/SMA50 Strategy Validation

## Research question

Can a simple, frozen BTC SMA20/SMA50 trend-following rule provide useful historical risk characteristics when evaluated out of sample?

The benchmark is passive BTC buy-and-hold over the same evaluation period.

## Verdict

**CAUTION — evidence of drawdown mitigation, not superior returns.**

The strategy returned **42.13%** out of sample versus **45.79%** for buy-and-hold. It reduced maximum drawdown from **-31.84% to -22.21%** and reduced volatility from **16.43% to 14.52%**.

The appropriate interpretation is **exposure management**, not demonstrated return alpha.

## Validation design

- Dataset: `BTC_history.csv`
- Development observations: 3,019
- Development end: 2022-12-22
- OOS observations: 1,295
- OOS period: 2022-12-23 to 2026-07-09
- Development fraction: 70%
- Warm-up: 50 bars
- Benchmark: buy-and-hold
- Strategy parameters: SMA20 / SMA50
- Strategy selection status: frozen for OOS validation

The OOS portfolio starts fresh at the evaluation boundary. Warm-up observations provide indicator context only.

## Main finding

The strategy sacrificed approximately **3.66 percentage points** of cumulative OOS return while improving maximum drawdown by approximately **9.63 percentage points**.

Its Sharpe ratio was numerically higher by **0.0139**, but this is not evidence of statistically significant risk-adjusted outperformance.

## Evidence

The complete machine-readable evidence is in `evidence/`.

See:

- `methodology/strategy_and_validation.md`
- `results/oos_validation.md`
- `results/cost_stress.md`
- `results/regime_analysis.md`
- `results/exposure_analysis.md`

## Limitations

This is historical research, not investment advice. The study does not establish future or live performance, cross-asset robustness, or return superiority. Complete real-world commission and fee modeling is not established by this evidence pack.
