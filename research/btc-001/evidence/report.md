# QuantLab BTC Strategy Validation Evidence Pack

## Executive Verdict

**VERDICT: CAUTION**

The frozen **BTC SMA20/SMA50 crossover** produced evidence of improved historical
risk characteristics out-of-sample, but it did **not** outperform buy-and-hold
in cumulative return.

Across the OOS period, the strategy returned **42.13%** versus
**45.79%** for buy-and-hold. Maximum drawdown was
**-22.21%** versus **-31.84%**, an improvement of
**9.63%**. Volatility was **14.52%** versus
**16.43%**, while Sharpe was **0.5263** versus
**0.5124**.

The appropriate interpretation is therefore **risk reduction / exposure
management**, not demonstrated return alpha.

---

## 1. Research Question

Can a simple, frozen BTC SMA20/SMA50 trend-following rule provide useful
historical risk characteristics when evaluated on data that was not used to
select or optimize the strategy?

The benchmark is passive BTC buy-and-hold over the same OOS period.

This pack is a research and audit artifact. It is not investment advice.

---

## 2. Strategy Specification

The strategy is a simple daily moving-average crossover:

- Fast moving average: **20-day simple moving average**
- Slow moving average: **50-day simple moving average**
- Long when SMA20 > SMA50
- Flat when SMA20 < SMA50
- No parameter optimization was performed after observing the OOS results
- Signal execution follows the QuantLab backtest engine's one-bar execution
  convention
- Position size: 1 BTC unit in the underlying backtest model
- Initial capital: $100,000
- Commission: $0 in this validation run
- Slippage: 0 in the base validation run

The strategy was evaluated as frozen. The OOS result was not used to tune
the parameters.

---

## 3. Data and Chronological Validation

Dataset: `BTC_history.csv`

Chronological split:

- Development fraction: 70%
- Development observations: **3,019**
- Development end: **2022-12-22 00:00:00**
- OOS observations: **1,295**
- OOS start: **2022-12-23 00:00:00**
- OOS end: **2026-07-09 00:00:00**
- Warm-up bars: **50**

The holdout evaluation begins at the stated OOS boundary. Warm-up observations
are used only for indicator context; pre-OOS signals are neutralized so that
the holdout portfolio starts fresh.

---

## 4. OOS Performance

| Metric | SMA20/SMA50 | Buy & Hold | Difference |
|---|---:|---:|---:|
| Total return | 42.13% | 45.79% | -3.66% |
| Annualized return | 6.81% | 7.32% | - |
| Sharpe ratio | 0.5263 | 0.5124 | 0.0139 |
| Maximum drawdown | -22.21% | -31.84% | 9.63% |
| Volatility | 14.52% | 16.43% | -1.91% |

### Interpretation

The strategy surrendered approximately **3.66 percentage points** of cumulative
return relative to buy-and-hold, while reducing maximum drawdown by approximately
**9.63 percentage points**.

That is a meaningful historical risk trade-off, but it is not evidence that the
strategy creates superior returns.

---

## 5. Exposure and Holding-Period Analysis

During the OOS period:

- Observations: **1,295**
- Invested days: **744**
- Flat days: **551**
- Exposure: **57.45%**
- Flat: **42.55%**
- Entries: **17**
- Exits: **17**
- Completed trades: **17**
- Open position at OOS end: **No**

The system was therefore exposed to BTC for approximately **57.45%** of the
OOS observations and flat for approximately **42.55%**.

This exposure reduction is an important part of the mechanism behind the lower
drawdown.

### Holding-period observations

There were **17 completed OOS holding periods**.

The largest recorded positive price-return periods included approximately:

- 2023-10-02 -> 2024-01-25: **+45.05%**
- 2024-02-12 -> 2024-04-20: **+30.10%**
- 2024-09-26 -> 2025-01-06: **+56.61%**

The system also experienced substantial losing periods, including:

- 2024-05-26 -> 2024-06-26: **-11.25%**
- 2024-07-29 -> 2024-08-15: **-13.86%**
- 2025-01-22 -> 2025-02-17: **-7.60%**
- 2026-01-09 -> 2026-02-03: **-16.44%**

This demonstrates that the strategy is **not crash-proof** and can lose
substantially during rapid reversals.

---

## 6. Regime Analysis

Regimes were classified using historical BTC price relative to a 200-day SMA
and the direction of that SMA:

- **Bull:** Close above SMA200 and SMA200 rising versus 30 days earlier
- **Bear:** Close below SMA200 and SMA200 falling
- **Sideways/transition:** all other observations

No future observations or OOS performance values were used to fit the regime
definition.

### Aggregate OOS regime results

| Regime | Episodes | Days | SMA Return | B&H Return | Difference |
|---|---:|---:|---:|---:|---:|
| Bear | 3 | 254 | -6.13% | -12.52% | **+6.39 pp** |
| Bull | 17 | 802 | +51.09% | +102.36% | **-51.28 pp** |
| Transition | 19 | 239 | +0.21% | -17.64% | **+17.86 pp** |

### Interpretation

The strongest relative behavior occurred during bear and transition conditions.

However, the strategy substantially lagged buy-and-hold during the aggregate bull
regimes. This is the principal economic cost of reducing exposure.

The transition category contains several short episodes, including one- to
three-day episodes, so its aggregate result should not be overinterpreted.

---

## 7. Slippage Stress

The frozen strategy was additionally evaluated under increasing slippage:

| Slippage | OOS Return | Annualized Return | Sharpe | Max Drawdown |
|---:|---:|---:|---:|---:|
| 0.00% | 42.13% | 6.81% | 0.5263 | -22.21% |
| 0.05% | 41.01% | 6.65% | 0.5151 | -22.38% |
| 0.10% | 39.89% | 6.49% | 0.5038 | -22.55% |
| 0.20% | 37.65% | 6.17% | 0.4811 | -22.89% |

Performance degrades gradually rather than collapsing under the tested
slippage levels.

**Important:** the QuantLab engine currently represents `commission` as an
absolute cash amount per transaction, not as a percentage of notional.
Therefore this stress test varies **slippage only** and does not claim to be
a complete realistic fee model.

---

## 8. What the Evidence Supports

The evidence supports the following statements:

1. The frozen SMA20/SMA50 strategy reduced OOS maximum drawdown relative to
   buy-and-hold.
2. It reduced OOS volatility.
3. It produced a slightly higher OOS Sharpe ratio.
4. It spent approximately 42.55% of OOS observations flat.
5. Its relative advantage was strongest in the observed bear and transition
   regimes.
6. Its performance degraded gradually under the tested slippage assumptions.

---

## 9. What the Evidence Does NOT Establish

This validation does **not** establish:

- superior long-run returns;
- persistent alpha;
- profitability after a complete real-world fee model;
- optimal SMA parameters;
- robustness across other assets;
- robustness across other time periods;
- immunity to rapid market reversals;
- future performance;
- live execution performance.

The parameters were intentionally not optimized after observing the OOS result.

---

## 10. Final Assessment

### CAUTION - Observed Risk Improvement; Return Superiority Not Demonstrated

The frozen BTC SMA20/SMA50 rule provides historical evidence of a
different risk/return profile from passive BTC exposure.

Its principal observed benefit was **drawdown and exposure management**, not
higher cumulative return.

For a buyer seeking a strategy that simply beats BTC buy-and-hold, this evidence
does not support a positive conclusion.

For a buyer evaluating whether a simple trend-following overlay can reduce
historical downside exposure while retaining substantial participation in
BTC trends, the evidence is materially more relevant.

---

## 11. Reproducibility

This pack preserves:

- the OOS summary;
- SMA strategy OOS equity curve;
- buy-and-hold OOS equity curve;
- corrected exposure summary;
- corrected position events;
- clean regime summary;
- clean regime episodes;
- SHA-256 hashes for all included artifacts.

The included CSV files are the frozen outputs used for the conclusions in this
report.

---

## 12. Evidence Inventory

See `manifest.json` for the complete machine-readable inventory and SHA-256
identities.

---

## 13. Research Limitation

This is a historical quantitative research artifact. It is not investment
advice, an offer to trade, or a guarantee of future results.
