# Backtest Evidence Pack — Pilot Specification

## Decision

QuantLab's first monetizable offer is a fixed-scope **Backtest Evidence Pack**
for an existing systematic crypto or liquid-market strategy.

The offer is a research-audit deliverable. It does not provide investment
advice, trading signals, performance guarantees, custody, brokerage access, or
execution authority.

## Buyer and Job

Initial buyer: an independent strategy builder, small research team, or
technical fund evaluating an existing rules-based strategy.

Job: "Before I spend more time, capital, or reputation on this strategy, give
me a reproducible account of what the supplied historical data and stated
rules actually support, what they do not support, and which assumptions could
invalidate the result."

## Paid Deliverable

Each pack contains:

1. declared strategy rules, parameters, instrument, time window, and costs;
2. input-data contract and validation result;
3. source-quality and Data Trust assessment, including unresolved issues;
4. deterministic backtest run and trade log;
5. return, volatility, drawdown, and risk-adjusted metrics;
6. a buy-and-hold comparison where appropriate;
7. limitations: market-data coverage, fees/slippage assumptions, execution
   model, overfitting risks, and non-represented market effects;
8. a reproducibility manifest: dataset identity, code revision, configuration,
   output paths, and rerun instructions.

The deliverable must label facts, inferences, and unresolved assumptions
separately. A passing test or completed run is not evidence of future returns.

## Why This Is the First Offer

QuantLab already has components for normalized OHLCV validation, a
capability-specific Data Trust gate, simple rules-based strategies, next-bar
backtesting, cost assumptions, metrics, and report exports. It does not yet
have the data coverage, provenance controls, live infrastructure, public API,
or authorization controls required to sell generic live market data, trading
signals, or execution.

The offer therefore monetizes a constrained research workflow rather than
claiming a broad platform capability.

## Pilot Boundary

### Included

- One client-supplied or explicitly licensed historical dataset.
- One deterministic, long-only, rules-based strategy.
- One stated asset or market universe.
- One specified period and parameter set.
- CSV evidence artifacts and a concise Markdown report.
- A human review checkpoint before any client-facing use.

### Excluded

- Live market data, intraday or order-book claims, or data resale.
- Strategy optimization, parameter search, or automated recommendation.
- Trade execution, broker connectivity, wallets, payments, or custody.
- Forecasts, target prices, personalized investment advice, or promised alpha.
- Public API, MCP server, agent-to-agent payment, or marketplace publication.

## Minimum Acceptance Criteria

A pilot result may be delivered only when all of the following are visible:

- dataset schema validation passes;
- the source quality is explicitly declared rather than silently defaulted;
- the data is suitable for the named backtest capability;
- configuration, code revision, dataset identity, and artifacts can be
  recorded for rerun;
- costs and execution timing are stated;
- the strategy is compared against a relevant baseline or the omission is
  explained;
- the report includes limitations and does not imply investability;
- a human approves the final client-facing wording.

Otherwise the correct output is a blocked or provisional evidence pack, not a
performance claim.

## Commercial Hypothesis

The first sale is a fixed-price pilot rather than a subscription. The initial
objective is evidence of willingness to pay, not scale.

Suggested validation sequence:

1. Produce one internally reviewed exemplar using a clearly licensed dataset.
2. Define a one-page scope, turnaround target, deliverable sample, and explicit
   exclusions.
3. Obtain five structured discovery conversations with strategy builders.
4. Ask for a paid pilot commitment before building a public interface.
5. Measure: qualified conversations, paid-pilot commitments, completion time,
   rerun success, and client-perceived decision value.

No outreach, price publication, collection of payment, customer commitment, or
data purchase is authorized by this document.

## Engineering Work Required Before an Exemplar

1. Route the experiment runner through `load_validated_dataset` or an
   equivalent single canonical boundary, with explicit `source_quality`.
2. Add a reproducibility manifest containing input file hash, code revision,
   configuration, trust assessment, and output hashes.
3. Add a comparison baseline to the experiment reporting path.
4. Audit and test multi-symbol next-bar semantics and enforce cash/exposure
   constraints for the stated long-only scope.
5. Run the full regression suite in a declared Python environment, then run a
   manually reviewed BTC exemplar.

These are trust and reproducibility requirements, not a mandate to build a
public platform.

## Stop Conditions

Stop and escalate before client use if dataset licensing is unclear, source
quality is unresolved, the requested strategy requires unsupported execution
assumptions, reproducibility artifacts cannot be generated, or the results
would be reasonably interpreted as personalized investment advice.
