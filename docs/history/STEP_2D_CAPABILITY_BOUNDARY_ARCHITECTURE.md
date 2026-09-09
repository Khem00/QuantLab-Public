# STEP 2D — CAPABILITY BOUNDARY ARCHITECTURE

Status: ARCHITECTURE / NOT YET AUTHORIZED FOR PRODUCTION IMPLEMENTATION
Branch: step-2d-next
Regression baseline: 159 passed

---

# 1. Purpose

Step 2D defines the public capability boundary of QuantLab.

The objective is not to expose the existing Python implementation as an API.

The objective is to define a deliberate, machine-readable, commercially consumable
capability layer through which AI agents and humans can discover, evaluate, invoke,
verify, and pay for QuantLab financial-intelligence capabilities without needing to
understand or access QuantLab's internal implementation.

This document therefore defines:

- what QuantLab exposes;
- what QuantLab deliberately does not expose;
- how AI agents discover capabilities;
- how humans discover capabilities;
- what evidence and trust information accompanies results;
- how authorization and side effects are controlled;
- how capabilities qualify for implementation;
- how observed paid demand governs the capability roadmap;
- when data acquisition or licensing becomes economically justified;
- what Step 2D implementation is and is not authorized to begin.

---

# 2. Strategic Product Principle

QuantLab is being designed as an agent-native financial-intelligence platform.

Its primary strategic requirement is not simply to contain useful financial
functionality.

QuantLab must be:

- discoverable by AI agents and humans;
- machine-evaluable;
- machine-invocable;
- machine-verifiable;
- commercially consumable;
- trustworthy;
- auditable;
- measurable and meterable;
- capable of supporting paid consumption.

QuantLab therefore treats the public capability boundary as a product,
security, data-trust, and monetization boundary simultaneously.

---

# 3. Core Commercial Loop

QuantLab's capability roadmap shall be driven by continuous observation of real
market demand.

The governing loop is:

    OBSERVED PAID DEMAND
            ↓
    DEMAND VALIDATION
            ↓
    CAPABILITY DEFINITION
            ↓
    TRUST / DATA / SECURITY / ECONOMIC GATES
            ↓
    MINIMUM VIABLE CAPABILITY
            ↓
    FIRST CUSTOMER / REVENUE
            ↓
    IDENTIFICATION OF INDISPENSABLE DATA
            ↓
    JUSTIFIED DATA ACQUISITION OR LICENSING
            ↓
    IMPROVED CAPABILITY
            ↓
    EXPANSION

QuantLab must not reverse this sequence unnecessarily by purchasing expensive
data, building large infrastructure, or implementing speculative capabilities
before evidence of commercial demand exists.

"Interesting" is not equivalent to "commercially validated."

A capability should have a documented demand hypothesis and a plausible
willingness-to-pay path before production implementation.

---

# 4. Continuous Paid-Demand Discovery

Paid-demand discovery is an ongoing QuantLab capability-governance mechanism.

QuantLab shall continuously investigate:

1. what AI agents are attempting to accomplish;
2. what humans are attempting to accomplish;
3. what financial-information tasks are already being paid for;
4. what existing tools, APIs, datasets, research products, or analysts are being
   purchased;
5. where users experience unmet needs or unacceptable friction;
6. what information is repeatedly requested;
7. what outputs users require;
8. what evidence users require to trust those outputs;
9. how frequently the demand occurs;
10. what users are willing or already able to pay;
11. whether QuantLab can solve the problem materially better or more efficiently;
12. what data is necessary to satisfy the demand;
13. whether the required data can be obtained lawfully and economically.

Demand discovery does not automatically authorize implementation.

Each demand becomes a candidate capability and must pass the appropriate gates.

---

# 5. Public Capability Boundary

The public boundary is the interface between QuantLab and external consumers.

External consumers include:

- AI agents;
- agent frameworks;
- software developers;
- financial applications;
- research systems;
- human users;
- organizations;
- future authorized trading or execution actors.

The public boundary shall expose capabilities rather than implementation details.

A capability should communicate at minimum:

- capability identity;
- purpose;
- supported inputs;
- supported outputs;
- limitations;
- evidence requirements;
- data provenance;
- trust state;
- freshness where relevant;
- authorization requirements;
- pricing or metering model where applicable;
- version;
- availability status;
- applicable usage limits;
- machine-readable error semantics.

---

# 6. Agent-Native Consumption Requirement

An AI agent consuming QuantLab must NOT be required to:

- clone the QuantLab GitHub repository;
- install the QuantLab source distribution merely to discover a capability;
- inspect Python source code;
- reverse-engineer internal implementation;
- understand pandas DataFrames;
- infer undocumented data structures;
- understand internal Python classes;
- understand internal module organization;
- reproduce QuantLab's internal execution pipeline;
- inspect tests to determine how a capability works;
- depend on private implementation details.

The desired interaction is:

    AGENT
      ↓
    DISCOVER CAPABILITY
      ↓
    READ MACHINE-READABLE CONTRACT
      ↓
    EVALUATE FIT / PRICE / TRUST / LIMITATIONS
      ↓
    REQUEST AUTHORIZATION IF REQUIRED
      ↓
    INVOKE CAPABILITY
      ↓
    RECEIVE STRUCTURED RESULT
      ↓
    VERIFY EVIDENCE / PROVENANCE / TRUST
      ↓
    PAY / METER CONSUMPTION

This boundary is fundamental.

QuantLab's internal implementation is an implementation concern, not a
customer integration contract.

---

# 7. Human Consumption Boundary

Humans may consume the same underlying capabilities through human-oriented
interfaces.

Human-facing interfaces may provide:

- readable explanations;
- charts;
- reports;
- research workflows;
- portfolio views;
- interactive analysis;
- capability discovery;
- pricing information;
- documentation.

However, human interfaces must consume the same underlying capability,
evidence, trust, authorization, and data layers as agent-facing interfaces.

QuantLab should not maintain contradictory business logic for agents and humans.

---

# 8. Capability Layers

The capability universe is divided into conceptual domains.

## 8.1 Data Intelligence

Examples:

- market-data retrieval;
- dataset discovery;
- dataset quality assessment;
- data trust assessment;
- historical data access;
- data freshness assessment;
- provenance inspection.

## 8.2 Market Intelligence

Examples:

- market state analysis;
- price/return analysis;
- volatility analysis;
- market regime analysis;
- anomaly detection;
- cross-asset analysis.

## 8.3 Research Intelligence

Examples:

- financial research;
- asset research;
- strategy research;
- evidence synthesis;
- research comparison;
- historical performance analysis.

## 8.4 Signal Intelligence

Examples:

- signal generation;
- signal validation;
- signal diagnostics;
- signal comparison.

Signals must not automatically imply investment advice or execution authority.

## 8.5 Portfolio Intelligence

Examples:

- portfolio analytics;
- allocation analysis;
- portfolio risk;
- performance attribution;
- drawdown analysis;
- portfolio comparison.

## 8.6 Risk Intelligence

Examples:

- risk measurement;
- stress analysis;
- exposure analysis;
- concentration analysis;
- risk diagnostics.

Risk intelligence may advise and challenge but must not silently bypass deterministic
risk controls.

## 8.7 Strategy Intelligence

Examples:

- strategy definition;
- strategy analysis;
- strategy comparison;
- backtesting;
- robustness analysis;
- experiment analysis.

Research results do not automatically become production strategies.

## 8.8 Event / Evidence Intelligence

Examples:

- financial-event analysis;
- evidence retrieval;
- source comparison;
- claim verification;
- provenance tracking.

## 8.9 Simulation Intelligence

Examples:

- historical simulation;
- scenario analysis;
- portfolio simulation;
- strategy simulation.

## 8.10 Trading / Execution Capabilities

Trading capabilities are a distinct class.

They may eventually include:

- trade proposals;
- order preparation;
- execution requests;
- execution monitoring;
- post-trade analysis.

Trading capabilities require substantially stronger authorization and governance
than read-only analytical capabilities.

Reasoning, trade proposals, risk controls, authorization, and execution must
remain separate stages.

---

# 9. Public Capability vs Internal Implementation

The following distinction is mandatory.

| Public capability | Internal implementation |
|---|---|
| Financial research | Python modules |
| Portfolio analysis | pandas operations |
| Backtesting | BacktestEngine internals |
| Strategy comparison | StrategyComparisonRunner internals |
| Data trust assessment | internal validation functions |
| Risk analysis | internal calculation functions |
| Market analytics | internal feature modules |
| Structured result | internal Python objects |
| Evidence | internal storage/retrieval mechanisms |
| Authorization | internal control implementation |

Internal implementation may change without breaking the public capability contract.

The public contract is therefore an abstraction boundary.

---

# 10. Current Repository Interpretation

The current repository inventory demonstrates why this boundary is required.

Current internal functionality includes:

- BacktestEngine;
- Portfolio;
- BacktestResult;
- Trade and TradeLog;
- ExperimentConfig;
- ExperimentRunner;
- StrategyComparisonRunner;
- ResearchReportGenerator;
- strategy implementations;
- data loading;
- normalization;
- validation;
- trust assessment;
- technical indicators;
- momentum calculations;
- returns calculations;
- volatility calculations;
- portfolio risk;
- reports;
- charts.

These are implementation assets.

They are NOT automatically public QuantLab capabilities.

The existence of a Python function or class does not imply that it should become
an external API.

---

# 11. Capability Contract Principle

Every production capability intended for external consumption must have an
explicit contract.

A capability contract should define:

- stable capability identifier;
- semantic version;
- purpose;
- input contract;
- output contract;
- validation rules;
- error contract;
- trust requirements;
- evidence requirements;
- provenance requirements;
- data freshness requirements where applicable;
- authorization requirements;
- side-effect classification;
- pricing/metering classification;
- limitations;
- reproducibility requirements.

Internal implementation details must not form part of the contract unless
explicitly designated as stable.

---

# 12. Evidence and Trust Boundary

Financial intelligence must not be treated as trustworthy merely because a
calculation completed successfully.

Where applicable, a capability result should preserve:

- source;
- provenance;
- timestamp;
- data version;
- methodology;
- assumptions;
- limitations;
- validation state;
- trust state;
- relevant warnings;
- reproducibility information.

Questionable or untrusted financial data must not silently become customer-facing
intelligence.

The unresolved Gold source-quality investigation remains an architectural
constraint.

---

# 13. Commercial Qualification Gate

A candidate capability must be evaluated against commercial evidence.

Minimum questions:

1. Is there observable demand?
2. Is the demand recurring or strategically significant?
3. Is someone already paying for an equivalent or adjacent solution?
4. Is there evidence that the problem is sufficiently painful?
5. Can QuantLab provide a materially useful solution?
6. Can the capability be delivered within acceptable trust and security boundaries?
7. Can the capability produce a viable economic path?
8. Can the capability be discovered by its intended consumers?
9. Can consumption be measured?
10. Is there a plausible route to first revenue?

Capabilities with weak demand evidence should normally remain research
candidates rather than becoming production priorities.

---

# 14. Data Acquisition / Licensing Gate

QuantLab must not assume that owning more data creates more value.

Data acquisition should follow demonstrated demand where practical.

The preferred sequence is:

    Demand
      ↓
    Customer requirement
      ↓
    Minimum viable data requirement
      ↓
    Revenue evidence
      ↓
    Data economics
      ↓
    License / acquire
      ↓
    Capability expansion

Before acquiring or licensing expensive financial data, QuantLab should establish:

- which capability requires it;
- which customer segment requires it;
- whether customers are willing to pay;
- expected consumption;
- expected revenue;
- licensing restrictions;
- redistribution restrictions;
- permitted use;
- storage requirements;
- attribution requirements;
- geographic restrictions;
- derivative-data restrictions where relevant;
- expected gross margin;
- scalability implications.

Licensing is therefore an economic decision, not merely a technical decision.

---

# 15. Security Boundary

QuantLab shall assume that external agents and consumers are not inherently
trusted.

The platform must be designed so that capability consumption does not require
revealing internal architecture.

External consumers should receive only what is necessary to:

- discover;
- evaluate;
- invoke;
- verify;
- consume;
- pay for

the capability.

Internal source code, internal dependency structure, private data locations,
credentials, internal control logic, and implementation-specific mechanisms
must remain outside the public capability boundary.

Authorization must be explicit.

Capabilities with external side effects require stronger controls than
read-only capabilities.

---

# 16. Capability Classes by Risk

| Class | Example | External side effect | Default posture |
|---|---|---:|---|
| C0 | Capability discovery | No | Publicly discoverable |
| C1 | Read-only analytics | No | Publicly consumable subject to contract |
| C2 | Research / simulation | No | Consumable with trust/evidence controls |
| C3 | Sensitive portfolio/risk analysis | No | Authenticated / authorized |
| C4 | Trade proposal | Potential | Strong authorization |
| C5 | Order preparation | Yes / potential | Strong authorization + deterministic controls |
| C6 | Execution | Yes | Explicit authorization + risk controls + audit |

No capability may escalate its authority merely because an agent successfully
invoked a lower-risk capability.

---

# 17. Discovery Boundary

QuantLab should eventually be discoverable through machine-readable mechanisms.

Discovery should allow an agent to determine:

- what QuantLab does;
- what capabilities exist;
- what each capability costs;
- what data each capability covers;
- what evidence accompanies results;
- what trust guarantees exist;
- what limitations apply;
- what authorization is required;
- how to invoke the capability.

Discovery should minimize unnecessary human interaction.

The objective is not simply "having an API."

The objective is making QuantLab understandable and evaluable by an AI agent.

---

# 18. Monetization Boundary

QuantLab should support consumption-based economics where appropriate.

The platform should be capable of measuring:

- capability calls;
- data volume;
- computation;
- report generation;
- research tasks;
- agent usage;
- API usage;
- successful outputs;
- authorized high-value operations.

Pricing must be attached to economically meaningful units of value rather than
arbitrary technical complexity.

The pricing model remains a commercial decision and must be validated against
observed demand.

---

# 19. Capability Lifecycle

Every capability follows a controlled lifecycle:

    OBSERVED
       ↓
    HYPOTHESIS
       ↓
    VALIDATED DEMAND
       ↓
    ARCHITECTED
       ↓
    TRUST / DATA / SECURITY REVIEW
       ↓
    IMPLEMENTATION AUTHORIZED
       ↓
    INTERNAL IMPLEMENTATION
       ↓
    CONTRACT VALIDATION
       ↓
    PRIVATE / EARLY CONSUMPTION
       ↓
    PAID VALIDATION
       ↓
    GENERAL AVAILABILITY
       ↓
    MONITORING
       ↓
    ITERATION / EXPANSION / RETIREMENT

A capability may remain in OBSERVED, HYPOTHESIS, or VALIDATED DEMAND without
production implementation.

---

# 20. Capability Boundary Matrix

| Domain | Candidate public capability | Intended consumer | Demand gate | Trust/evidence gate | Data/licensing gate | Side-effect risk | Step 2D implementation authorization |
|---|---|---|---|---|---|---|---|
| Discovery | Capability discovery | Agents/humans | Required | Required | N/A | None | Architecture only |
| Data | Data intelligence | Agents/humans | Required | Required | Required | None | Architecture only |
| Market | Market intelligence | Agents/humans | Required | Required | Required | None | Architecture only |
| Research | Research intelligence | Agents/humans | Required | Required | Required | None | Architecture only |
| Signals | Signal intelligence | Agents/humans | Required | Required | Required | Low | Architecture only |
| Portfolio | Portfolio intelligence | Humans/agents | Required | Required | Required | Low | Architecture only |
| Risk | Risk intelligence | Humans/agents | Required | Required | Required | Medium | Architecture only |
| Strategy | Strategy intelligence | Agents/humans | Required | Required | Required | Low | Architecture only |
| Simulation | Simulation intelligence | Agents/humans | Required | Required | Required | Low | Architecture only |
| Evidence | Evidence/claim verification | Agents/humans | Required | Strong | Required | Low | Architecture only |
| Trading | Trade proposals | Authorized agents/humans | Strong | Strong | Required | High | Not authorized |
| Execution | Order execution | Authorized actors | Strong | Strong | Required | Critical | Not authorized |

---

# 21. What Step 2D Does NOT Authorize

Step 2D does NOT authorize:

- building a public API;
- building an MCP server;
- creating agent authentication;
- creating billing infrastructure;
- purchasing expensive financial datasets;
- entering data-licensing agreements;
- exposing internal Python classes;
- exposing internal pandas schemas as customer contracts;
- building trading execution;
- connecting to exchanges for live execution;
- converting research into investment advice;
- converting strategies into autonomous trading authority;
- creating customer-facing production infrastructure.

Those activities require subsequent architectural and implementation decisions.

---

# 22. What Step 2D May Authorize Later

After successful validation, a subsequent implementation checkpoint may authorize
limited work such as:

- formalizing capability definitions;
- defining machine-readable contracts;
- building a capability registry;
- creating discovery metadata;
- establishing internal capability adapters;
- creating contract tests;
- creating demand-evidence records;
- implementing metering abstractions;
- creating controlled read-only interfaces.

Such work must remain within the explicitly approved scope.

---

# 23. Validation Criteria

Step 2D architecture is considered valid only if:

1. Every proposed public capability has a clear consumer.
2. Every capability has a defined boundary from internal implementation.
3. AI agents can conceptually consume capabilities without source inspection.
4. Human and agent consumers can use the same underlying capability layer.
5. Trust and evidence are part of the capability boundary.
6. Paid demand influences capability prioritization.
7. Data acquisition is governed by commercial evidence.
8. Licensing requirements are explicitly considered.
9. High-risk side effects have stronger authorization requirements.
10. Trading and execution remain separate from research.
11. Internal classes and pandas structures are not treated as public contracts.
12. Capability discovery is machine-oriented.
13. Monetization and metering are architectural concerns.
14. The unresolved Gold-data issue remains preserved.
15. No production implementation is implicitly authorized merely by defining
    the architecture.

---

# 24. Validation Against Current Repository

The current repository inventory demonstrates that QuantLab already contains
useful internal analytical primitives.

However, the inventory does not by itself establish which primitives should
become public capabilities.

Current package exports are intentionally limited.

Therefore:

    INTERNAL FUNCTIONALITY ≠ PUBLIC CAPABILITY

The Step 2D architecture introduces a deliberate capability layer above the
existing implementation.

The implementation question is deferred until capability demand and contract
requirements are sufficiently validated.

---

# 25. Architectural Decision

QuantLab will not optimize primarily for the number of functions, models,
datasets, strategies, or APIs it exposes.

QuantLab will optimize for the number and quality of economically valuable
financial-intelligence jobs it can reliably solve for humans and AI agents.

The capability roadmap shall therefore be governed by:

    CUSTOMER / AGENT NEED
          +
    PAID DEMAND
          +
    TRUST
          +
    DATA AVAILABILITY
          +
    SECURITY
          +
    ECONOMICS
          +
    DISCOVERABILITY

A capability is valuable when it solves a meaningful problem and can be
reliably consumed and commercially exchanged.

---

# 26. Step 2D Status

Architecture status:

CAPABILITY BOUNDARY DEFINED — PENDING VALIDATION

Production implementation:

NOT AUTHORIZED

Data acquisition / licensing:

NOT AUTHORIZED

Trading execution:

NOT AUTHORIZED

Public API implementation:

NOT AUTHORIZED

Agent integration implementation:

NOT AUTHORIZED

Required next activity:

Validate this document against:

- the existing repository inventory;
- the Step 2C architecture;
- the 159-test regression baseline;
- the agent-native product strategy;
- the continuous paid-demand discovery strategy;
- the Data Trust Engineering principles;
- security and authorization boundaries.

After validation, record the Step 2D checkpoint in PROJECT_STATE.md.

Only then may an explicit implementation authorization decision be made.

---

# 27. Governing Principle

QuantLab should not ask:

"How much financial functionality can we build?"

QuantLab should ask:

"What financial-intelligence problems are AI agents and humans already
willing to pay to solve, and what is the smallest trustworthy capability
QuantLab can provide to solve them?"

The resulting sequence is:

    PAID DEMAND
       ↓
    CAPABILITY
       ↓
    CUSTOMER
       ↓
    REVENUE
       ↓
    INDISPENSABLE DATA
       ↓
    JUSTIFIED LICENSING
       ↓
    BETTER CAPABILITY
       ↓
    EXPANSION

This is the governing commercial and architectural loop for Step 2D.
