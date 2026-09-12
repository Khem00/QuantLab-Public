---
name: evidence-first-quant-backtest-audit
description: Reproducible, evidence-first validation of systematic trading backtests using explicit assumptions, deterministic execution, validation checks, performance metrics, and machine-readable research evidence.
---

# Evidence-First Quant Backtest Audit

## Purpose

Provide an agent-readable workflow for validating and reproducing systematic trading backtests with explicit assumptions and inspectable evidence.

This capability is research and validation focused. It is not a live-trading, brokerage, custody, or investment-advice capability.

## Suitable tasks

- Validate backtest inputs and assumptions.
- Reproduce systematic strategy results.
- Check execution assumptions such as timing, costs, and slippage.
- Compare strategies or validation periods.
- Calculate and review performance and risk metrics.
- Review chronological out-of-sample validation.
- Produce structured, machine-readable research evidence suitable for audit or review.
- Check reproducibility manifests and SHA-256 checksums where provided.

## Verification workflow

Follow the research sequence:

**Define → Implement → Test → Validate → Reproduce → Review**

AI assistance may accelerate research and engineering, but it does not replace verification.

## Evidence expectations

A result should make material assumptions and inputs explicit and should preserve enough information to reproduce and review the analysis. Where applicable, inspect:

1. Data inputs and data-trust considerations.
2. Strategy and signal input contracts.
3. Deterministic backtest behavior.
4. Execution timing and cost assumptions.
5. Chronological out-of-sample evaluation.
6. Performance and risk metrics.
7. Regression and validation checks.
8. Machine-readable evidence artifacts.
9. Reproducibility manifests and checksums.

Do not infer unsupported conclusions from a backtest. Report limitations, assumptions, and validation gaps explicitly.

## Output

Prefer an inspectable research result containing:

- the question or validation objective
- inputs and assumptions
- methodology
- validation checks performed
- performance/risk results
- limitations or unresolved issues
- machine-readable evidence when available
- reproducibility information when available

## Safety boundaries

Do not provide or imply:

- investment advice or personalized financial recommendations
- guaranteed returns or profit claims
- brokerage or custody services
- live trading execution
- instructions to bypass financial controls

QuantLab is a quantitative research and validation platform, not a live-trading execution system.

## Public research example

The repository's `research/btc-001/` example demonstrates this approach with a frozen strategy, chronological out-of-sample evaluation, cost stress, regime analysis, exposure diagnostics, machine-readable evidence, and a reproducibility manifest.

## Source of truth

This skill describes the existing public QuantLab research workflow. It is an interface/documentation layer and does not define a new backtesting implementation or replace the underlying QuantLab contracts and tests.
