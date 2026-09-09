# QuantLab

**AI-assisted quantitative research with reproducible, evidence-first validation.**

QuantLab is a Python-based quantitative research and financial analysis platform
designed to turn market data and research ideas into testable, reproducible
evidence.

The project combines quantitative research, financial data validation,
deterministic backtesting, risk analysis, automated testing, and AI-assisted
engineering.

The central principle is:

> **AI can accelerate research and engineering. Verification determines
> whether the resulting financial evidence deserves trust.**

## What QuantLab Demonstrates

QuantLab brings together three connected areas of work:

### 1. Quantitative and Financial Research

- Financial market data loading and normalization
- Data validation and data-trust assessment
- Quantitative experiments
- Rules-based strategy research
- Deterministic backtesting
- Portfolio valuation and performance analysis
- Risk and trade statistics
- Benchmark comparison

### 2. AI-Assisted Reproducible Engineering

AI is used as an engineering and research aid rather than as an authority on
financial results.

Research workflows are built around:

- Explicit data and strategy contracts
- Deterministic execution
- Automated regression testing
- Validation before interpretation
- Reproducible artifacts
- Documented assumptions and limitations
- Human review

The workflow is:

**Define → Implement → Test → Validate → Reproduce → Review**

See [`ai/`](ai/) for the AI-assisted reproducibility approach.

### 3. Evidence-First Strategy Validation

QuantLab treats a backtest as an evidence-generation process rather than simply
a performance number.

Validation can include:

- Chronological development/holdout separation
- Out-of-sample evaluation
- Benchmark comparison
- Execution and cost assumptions
- Cost-stress analysis
- Exposure analysis
- Regime analysis
- Machine-readable evidence artifacts
- SHA-256 integrity checks
- Reproducibility manifests
- Explicit research limitations

## BTC #001 — Reproducible Strategy Validation

[`research/btc-001/`](research/btc-001/) contains a complete public research
example.

The study evaluates a frozen **BTC SMA20/SMA50 crossover** against
buy-and-hold using chronological out-of-sample validation.

The OOS period runs from **2022-12-23 to 2026-07-09**.

### Headline result

| Metric | SMA20/SMA50 | Buy & Hold |
|---|---:|---:|
| Total return | 42.13% | 45.79% |
| Sharpe ratio | 0.5263 | 0.5124 |
| Maximum drawdown | -22.21% | -31.84% |
| Volatility | 14.52% | 16.43% |

The strategy therefore **did not demonstrate superior cumulative returns**.

It did, however, show lower historical maximum drawdown and volatility over
the OOS period.

The resulting interpretation is:

> **CAUTION — the evidence is more consistent with exposure management and
> historical risk reduction than with demonstrated return alpha.**

The study deliberately avoids claiming profitability, persistent alpha,
future performance, or cross-asset robustness.

## Reproducible Evidence

The BTC #001 evidence directory contains:

- OOS performance summaries
- Strategy and benchmark equity curves
- Exposure diagnostics
- Position events
- Regime summaries
- Regime episodes
- A research report
- A machine-readable manifest
- SHA-256 checksums

The evidence files are designed to make the reported result inspectable and
reproducible rather than dependent on a screenshot or a single performance
number.

## Current Research Infrastructure

QuantLab currently includes:

- Market data ingestion and normalization
- Data validation and trust checks
- Experiment configuration and execution
- Deterministic research workflows
- Rules-based backtesting
- Multi-symbol portfolio valuation
- Commission and slippage handling
- Long-only strategy constraints
- Next-bar execution semantics
- Portfolio returns, risk, and trade statistics
- Strategy and signal input contracts
- Chronological holdout validation
- Evidence-pack generation
- Automated regression and contract tests

The current test suite collects **190 tests**.

## Evidence Pack

QuantLab's first commercial research offer is a fixed-scope:

**Backtest Evidence Pack**

The objective is to provide a reproducible account of what a supplied
strategy and historical dataset actually demonstrate.

A typical pack can contain:

- Strategy specification
- Dataset and data-trust assessment
- Deterministic backtest results
- Benchmark comparison
- Performance and risk metrics
- Execution and cost assumptions
- Reproducibility information
- Machine-readable evidence
- Limitations and a research verdict
- Human review before client-facing use

The Evidence Pack is a **validation and research service, not investment
advice or a promise of future returns**.

See [`docs/BACKTEST_EVIDENCE_PACK_PILOT.md`](docs/BACKTEST_EVIDENCE_PACK_PILOT.md).

## Technology

- **Python 3.11**
- pandas
- NumPy
- pytest
- Ruff
- Black
- Jupyter
- Git
- Local AI development tooling

## Repository Structure

```text
QuantLab/
├── ai/
│   └── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── BACKTEST_EVIDENCE_PACK_PILOT.md
│   └── history/
├── research/
│   └── btc-001/
│       ├── methodology/
│       ├── results/
│       └── evidence/
├── scripts/
├── src/
│   └── quantlab/
│       ├── backtest/
│       ├── data/
│       ├── experiments/
│       ├── features/
│       ├── portfolio/
│       ├── reports/
│       ├── signals/
│       └── strategies/
├── tests/
├── pyproject.toml
├── pytest.ini
├── requirements-dev.txt
├── .gitignore
└── README.md
