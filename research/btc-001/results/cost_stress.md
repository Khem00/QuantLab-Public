# Cost Stress

The base OOS validation used zero commission and zero slippage.

A separate slippage stress tested:

- 0.00%
- 0.05%
- 0.10%
- 0.20%

The results showed gradual performance degradation as slippage increased rather than an abrupt collapse.

| Slippage | OOS return | Annualized return | Sharpe | Max drawdown | Volatility |
|---:|---:|---:|---:|---:|---:|
| 0.00% | 42.13% | 6.81% | 0.5263 | -22.21% | 14.52% |
| 0.05% | 41.01% | 6.65% | 0.5151 | -22.38% | 14.56% |
| 0.10% | 39.89% | 6.49% | 0.5038 | -22.55% | 14.60% |
| 0.20% | 37.65% | 6.17% | 0.4811 | -22.89% | 14.69% |

Important limitation: the current engine models commission as an absolute cash amount per transaction, so this study varied slippage only. It should not be described as complete real-world transaction-cost modeling.

The canonical evidence pack records the cost-stress assumptions in its manifest.
