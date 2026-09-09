# Strategy and Validation Methodology

## Strategy

BTC daily SMA20/SMA50 crossover:

- Long when SMA20 > SMA50
- Flat when SMA20 < SMA50
- Fast period: 20 days
- Slow period: 50 days
- Parameters frozen before OOS evaluation

No parameter optimization was performed after observing OOS results.

## Backtest assumptions

- Initial capital: $100,000
- Position size: 1 BTC unit in the underlying backtest model
- Base commission: $0
- Base slippage: 0
- Signal execution follows QuantLab's one-bar execution convention

## Chronological validation

The dataset was divided chronologically:

- Development: 3,019 observations
- Development end: 2022-12-22
- OOS: 1,295 observations
- OOS start: 2022-12-23
- OOS end: 2026-07-09
- Development fraction: 70%
- Warm-up: 50 bars

Warm-up observations are retained for indicator context. Pre-OOS signals are neutralized and the OOS portfolio starts fresh at the evaluation boundary.

## Benchmark

Performance is compared with passive BTC buy-and-hold over the same OOS period.

## Evidence chain

The `evidence/` directory contains the machine-readable OOS summary, equity curves, exposure analysis, regime analysis, manifest, research report, and SHA-256 checksums.

## Limitations

The evidence is historical only. It does not establish future performance, live execution performance, cross-asset robustness, or investment suitability. Complete real-world commission and fee modeling is not established by this study.
