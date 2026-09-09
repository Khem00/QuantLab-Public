# Regime Analysis

Regimes were classified using BTC price relative to its 200-day SMA and the direction of that SMA over a 30-day lookback.

## Aggregate results

| Regime | Episodes | Days | SMA return | Buy & Hold return | Difference | SMA volatility | Buy & Hold volatility | SMA max drawdown | Buy & Hold max drawdown |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Bear | 3 | 254 | -6.13% | -12.52% | +6.39 pp | 13.51% | 20.65% | -15.31% | -21.31% |
| Bull | 17 | 802 | +51.09% | +102.36% | -51.28 pp | 19.94% | 19.87% | -18.58% | -11.85% |
| Sideways/transition | 19 | 239 | +0.21% | -17.64% | +17.86 pp | 13.73% | 20.28% | -10.77% | -12.36% |

The strategy's strongest relative behavior occurred in bear and transition conditions, while it materially lagged buy-and-hold during bull conditions.

## Interpretation

This reinforces the exposure-management interpretation.

The rule can reduce downside exposure during prolonged weakness, but it can also sacrifice substantial upside during sustained bull markets and can experience losses during reversals.

It should not be described as crash-proof or as a superior all-regime strategy.

The underlying machine-readable evidence is in `evidence/regimes/`.
