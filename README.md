# QuantLab

QuantLab is a modular quantitative research and financial analysis platform built in Python. The project focuses on reproducible data workflows, validation, experimentation, backtesting, portfolio analytics, and quality-controlled research outputs.

## What QuantLab Demonstrates

- Python-based quantitative research and data analysis
- Financial market data loading and normalization
- Dataset validation and reproducibility checks
- Rules-based backtesting and portfolio valuation
- Automated testing with `pytest`
- AI-assisted software development and code review
- Structured investigation of implementation and data-quality issues
- Git-based incremental development and documented checkpoints

## Current Capabilities

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
- Automated regression and contract tests
- AI-agent tooling and permission/guard testing

The project is developed incrementally, with changes validated through automated tests and documented engineering checkpoints.

## Data

Research workflows have included datasets such as:

- Bitcoin (BTC)
- Apple (AAPL)
- Gold
- S&P 500
- VIX

## Technology

- **Python 3.11**
- pandas
- NumPy
- pytest
- Ruff
- Black
- Jupyter
- Git
- Qwen / DeepSeek / local AI tooling
- Ollama

## Quality & Validation

A major focus of QuantLab is making research results reproducible and testable rather than relying only on successful execution.

Development includes:

- Automated regression testing
- Data validation
- Reproducibility checks
- Contract and policy tests
- Investigation of discrepancies between expected and observed behavior
- Explicit documentation of implementation decisions
- Incremental Git checkpoints

The current test suite contains **216 automated tests**.

## AI-Assisted Development

QuantLab is also used as a practical environment for AI-assisted software development.

AI coding tools are used to assist with implementation, investigation, testing, and code review. Generated work is treated as something to be evaluated and validated rather than automatically trusted.

This includes checking AI-generated changes against project requirements, automated tests, expected behavior, and documented constraints.

## Repository Structure

```text
QuantLab/
├── data/
│   ├── raw/
│   └── processed/
├── models/
├── notebooks/
├── reports/
├── scripts/
├── src/
│   └── quantlab/
│       ├── backtest/
│       ├── data/
│       ├── experiments/
│       └── portfolio/
├── tests/
├── requirements-dev.txt
├── .gitignore
└── README.md