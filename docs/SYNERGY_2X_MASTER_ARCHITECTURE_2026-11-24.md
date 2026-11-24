# SYNERGY 2X — Master Architecture & Capability Portfolio

**Document ID:** SYNERGY-2X-MASTER-ARCH-2026-11-24  
**Version:** 0.1.0  
**Date:** 2026-11-24  
**Status:** Architecture proposal / implementation roadmap; not a production-readiness claim  
**Architecture authority:** `Shtenco/synergy_system`  
**Umbrella registry:** `Shtenco/synergy`  
**Economic master dossier:** `Shtenco/synergy_project`  
**Runtime orchestrator:** `Shtenco/synergy_meta_os`

---

## 1. Executive decision

SYNERGY 2X defines a portfolio of **30 distinct capability domains** across six business and technology divisions. It does not prescribe 30 new repositories, 30 deployed products, or 30 autonomous agents.

The current owner inventory is 92 repositories (16 public / 76 private) as recorded on 2026-11-20. The repository atlas states that 17 newly inventoried repositories remain provisional and that `synergy_maps` is a placeholder on main. The federation registry records 39 contract families, 44 runtime-adapter edges and **0 E2E-tested edges** as of the 2026-11-20 snapshot. These facts make architecture consolidation and evidence closure the first priority—not repository multiplication.

**Decision:** extend existing canonical repositories wherever their authority and scope fit. Create a new repository only when a capability has a genuinely independent bounded context, owner, release lifecycle, security boundary and acceptance suite.

This document is a portfolio map. An architectural mapping to a repository is not proof of code dependency, runtime integration, production deployment, legal authorization or commercial traction.

## 2. Design principles

1. **One authority per fact.** Every domain has a canonical owner for its records and state transitions.
2. **Proposal is not authorization.** AI may recommend or prepare an action; policy and a human or explicitly authorized service approve it.
3. **Ledger is the accounting authority.** UI state, blockchain events, model output and gross transaction volume do not independently establish accounting truth or external profit.
4. **Evidence before maturity.** Concept, prototype, tested component, integrated component, deployed service and commercial product are separate states.
5. **Contracts before coupling.** Cross-repository communication uses versioned schemas, explicit compatibility rules and conformance tests.
6. **Least privilege.** Agents receive narrow, revocable capabilities. A service supervisor cannot silently grant treasury, trading, identity or ledger authority.
7. **Fail closed for high-impact operations.** Stale state, missing evidence, policy uncertainty or unavailable risk controls must prevent irreversible financial execution.
8. **No double counting.** Shared identity, inference, audit, ledger, data and infrastructure costs are counted once in portfolio reporting.
9. **Human override and appeal.** Employment, credit, investment, medical, legal and identity decisions require explainability, review and appeal paths appropriate to their impact.
10. **No unsupported superiority claims.** “Fastest”, “best”, “global coverage”, “fully native” and similar claims require reproducible comparative evidence.

## 3. Canonical architecture

```text
                  PEOPLE / ORGANIZATIONS / PARTNERS
                               |
                    EXPERIENCE & WORKSPACE LAYER
          Human OS | Business OS | Investment Workspace
                               |
                    AGENT & INTELLIGENCE LAYER
       NEXUS | model inference | agents | memory | planning
                               |
                 POLICY / IDENTITY / AUTHORIZATION
        identity | roles | scopes | approvals | revocation
                               |
                    DOMAIN CAPABILITY SERVICES
    Business | Human | Capital | Quant | DeFi | Cooperative Economy
                               |
                    ECONOMIC SYSTEM OF RECORD
    double-entry ledger | obligations | contracts | settlement
                               |
                  TRUST / BLOCKCHAIN COMMITMENT
       signatures | attestations | proofs | ordered commitments
                               |
                 INFRASTRUCTURE & NODE RUNTIME
     META-OS | host OS | SynergyNet | storage | observability
```

The diagram expresses target responsibility boundaries, not an assertion that all layers are implemented or connected.

### 3.1 Canonical responsibility boundaries

| Concern | Proposed canonical authority | Explicit non-authority |
|---|---|---|
| Federation topology, contracts, security gates | `synergy_system` | Does not execute business workflows |
| Repository inventory and navigation | `synergy` | Does not own product source code |
| Node service lifecycle | `synergy_meta_os` | Does not grant financial authority |
| Host operating system | `synergy_turbo_linux` | Does not own domain accounting |
| P2P transport | `synergy_net` | Does not define settlement truth |
| AI model and agent proposals | NEXUS / AGI domain repositories | Model output is not authorization |
| Trading signal and portfolio proposal | MIDAS / Quant domain | Signal is not an order or realized P&L |
| Independent pre-trade risk veto | `synergy_riskguard` | Strategy cannot override DENY/KILL |
| Order routing and execution | TradeMux / approved execution adapter | Execution report is not accounting recognition |
| Payment / settlement evidence | Pay System | Payment evidence is not ledger posting |
| Financial recognition and balances | Financial OS / canonical ledger | UI and chain event are not ledger state |
| Economic theory and simulation | `synergistic_economics` and economic research repos | Simulation is not empirical proof |
| Civilizational research graph | `synergy_megaproject` | Research graph is not runtime dependency |

### 3.2 Shared data envelope

All inter-domain events should carry a common envelope (exact schema to be versioned in a separate contract):

- `event_id`: globally unique immutable event identifier;
- `event_type` and `schema_version`;
- `producer_id`, `tenant_id`, `actor_id` and optional `agent_id`;
- `occurred_at` and `recorded_at` in UTC;
- `correlation_id`, `causation_id` and `idempotency_key`;
- `subject_ref` and `source_revision`;
- `payload_hash` and evidence references;
- `policy_context` and authorization reference where relevant.

Events are append-only evidence. Corrections use compensating events; they do not silently rewrite history.

## 4. The 30 capability domains

The six divisions below contain exactly 30 distinct domains. Repository references are **candidate anchors** based on the current inventory and inspected README material. They do not imply a verified runtime edge.

Maturity labels:
- **EXISTING / VERIFY** — a relevant repository or implementation is present; revalidate current main, branches, tests and runtime.
- **PROTOTYPE / R&D** — code or research exists, but product-level claims remain gated.
- **GAP** — no sufficiently evidenced canonical implementation was identified in the inspected material.
- **RESEARCH** — research/simulation capability, not a production service.

### Division A — Autonomous Business

| # | Capability | Candidate canonical anchors | Initial product boundary | First acceptance evidence | Revenue model |
|---:|---|---|---|---|---|
| 1 | **CEO AI / Executive Copilot** | `synergy_ai_company`, `synergy_agi_nexus`, `synergy_agi_autopilot` | Decision support, scenario briefs, KPI explanations and approval queues; no autonomous authority to move money or hire/fire | Reproducible decision trace; source-linked recommendations; approval and rollback tests | Enterprise SaaS / deployment license |
| 2 | **Workforce & Agent Operations** | `synergy_ai_company`, `synergy_agi_autopilot`, `synergy_long_term_harness` | Work allocation, human/agent task lifecycle, leases, escalation and audit | Duplicate-task, expired-lease, unauthorized-action and human-escalation tests | Per-seat / per-agent SaaS |
| 3 | **Procurement Intelligence** | `synergy_lead_search_engline` (adjacent lead discovery; not procurement authority) | Supplier discovery, RFQ comparison, purchase recommendations and contract approval | Supplier provenance, quote normalization, conflict-of-interest checks, approval-gated purchase workflow | Subscription + workflow fee |
| 4 | **Supply Chain Control Tower** | GAP; integrate with `synergy_financial_os` and approved partner systems | Demand, inventory, supplier, shipment and disruption visibility | Reconciled inventory events, simulated disruption tests, forecast error and traceable source data | Enterprise SaaS / API |
| 5 | **Legal & Contract Operations AI** | GAP; shared identity/audit contracts from `synergy_system` | Drafting assistance, clause extraction, obligation calendar and risk triage; lawyer retains legal judgment | Clause-level citations, jurisdiction tagging, version comparison, human approval and access isolation | Per-seat / enterprise license |

### Division B — Human OS

| # | Capability | Candidate canonical anchors | Initial product boundary | First acceptance evidence | Revenue model |
|---:|---|---|---|---|---|
| 6 | **Life AI / Personal Operations** | `synergy_apps`, `synergy_app_family`, `sinergy_super_app` | User-controlled task, schedule, document and service orchestration | Consent, data export/deletion, action preview, permission revocation and recovery tests | Freemium / premium subscription |
| 7 | **Personal & Organizational Knowledge** | `synergy_hierarchical_cognitive_memory_architecture`, `synergy_long_term_harness`, `synergy_ai_coder` | Provenance-backed retrieval and task memory with separate authorities for knowledge, engineering evidence and mission lifecycle | Multi-tenant namespace isolation, source revision binding, symlink containment, retrieval provenance and deletion propagation | Storage / API / enterprise license |
| 8 | **Adaptive Education** | GAP; NEXUS may provide model services | Skills graph, learning plan, practice generation and mastery tracking | Held-out learning assessment, bias review, source attribution and learner data controls | B2C subscription / institutional license |
| 9 | **Health Information Assistant** | GAP; NEXUS may provide local inference | User-controlled document organization, appointment preparation and trend summaries; no autonomous diagnosis or treatment | Clinical safety review, source traceability, consent, privacy and explicit non-diagnostic behavior | Subscription / provider integration |
| 10 | **Digital Identity & Verifiable Credentials** | `synergy_ai_blockchain`, `synergy_chain`, `synergy_metachain` (candidate trust substrate) | Identifiers, credential issuance/verification, delegated agent authority and selective disclosure | Key lifecycle, revocation, replay protection, privacy threat model and independent cryptographic review | Verification API / enterprise identity |

### Division C — Capital & Investment

| # | Capability | Candidate canonical anchors | Initial product boundary | First acceptance evidence | Revenue model |
|---:|---|---|---|---|---|
| 11 | **Investment Intelligence** | `synergy_ai_investment_committee`, `synergy_midas_ai`, `synergy_financial_os` | Research, valuation models, scenario analysis and investment memo generation | Source provenance, valuation sensitivity, conflict disclosure and analyst review | Research subscription / enterprise license |
| 12 | **Venture & Private-Market Workflow** | GAP; connect to Investment Intelligence and Digital Identity | Deal room, diligence workflow, cap-table/rights records and investor reporting | Legal rights model, investor eligibility controls, audit trail and transfer restrictions | SaaS / administration fee |
| 13 | **Real-World Asset Lifecycle (RWA)** | `synergy_ai_blockchain`, `synergy_chain`, `synergy_pay_system` (candidate components) | Asset registry, evidence, servicing events and rights-linked token representation | Legal opinion per jurisdiction, custody/registry reconciliation, redemption and default tests | Issuance / servicing / API fees |
| 14 | **Treasury AI** | `synergy_financial_os`, `synergy_pay_system`, `synergy_blochain_budget` | Cash forecast, payment schedule, liquidity limits and scenario planning | Ledger reconciliation, cash forecast backtest, approval matrix and payment idempotency | Enterprise SaaS |
| 15 | **Portfolio Constructor** | `synergy_financial_os`, `synergy_midas_ai`, `synergy_quantlab` | Constrained portfolio construction, risk attribution and rebalancing proposals | Frozen data, OOS evaluation, turnover/cost modeling, constraints and benchmark comparison | Subscription / enterprise license |

### Division D — Quant & Market Intelligence

| # | Capability | Candidate canonical anchors | Initial product boundary | First acceptance evidence | Revenue model |
|---:|---|---|---|---|---|
| 16 | **Quant Lab / Strategy Research Factory** | `synergy_quantlab`, `synergy_midas_ai` | Hypothesis registry, reproducible backtests, walk-forward and multiple-testing controls | Dataset and commit hashes, frozen OOS, purge/embargo checks, bootstrap intervals and reproducible reports | Research platform license |
| 17 | **Market-Making Network** | `synergy_market_maker`, `synergy_adaptive_engine`, `synergy_midas_institutional` | Inventory-aware quoting and risk-bounded market-making research/execution | Fill-quality, adverse-selection, inventory, fees, latency and kill-switch evidence | License / approved performance fee where lawful |
| 18 | **Arbitrage Intelligence** | `synergy_market_graph`, `synergy_trademux`, `synergy_algotrading_graph_system` | Opportunity graph with executable-cost and settlement-risk estimates | Atomicity, stale quote, partial-fill, gas/fee, bridge and counterparty failure simulations | API / enterprise license |
| 19 | **Derivatives & Volatility Analytics** | `synergy_midas_institutional`, `synergy_midas_ai` (candidate research anchors) | Options/futures exposure, Greeks, volatility surface and scenario analytics | Independent pricing checks, market-data timestamps, stress scenarios and model-risk report | Data/API subscription |
| 20 | **Risk OS** | `synergy_riskguard` | Independent pre-trade and portfolio risk decision, deny/resize/kill path | Stale-state fail-closed, policy provenance, adversarial tests, signed decision trace and customer OOS/shadow evidence | Enterprise license / paid pilot |

### Division E — DeFi & Blockchain

| # | Capability | Candidate canonical anchors | Initial product boundary | First acceptance evidence | Revenue model |
|---:|---|---|---|---|---|
| 21 | **Universal DEX & Liquidity Router** | `synergy_chain`, `synergy_metachain`, `synergy_ai_blockchain`, AMM research repos | Route and settle supported swaps; separate quote, execution, settlement and accounting | Invariant/property tests, MEV/slippage analysis, chain-fork tests, audits and reconciliation | Protocol fees / integration license |
| 22 | **Credit Protocol** | `synergy_agentic_ai_economy`, `synergy_chain`, `synergistic_economics` | Collateralized and/or mutual-credit experiments with explicit underwriting and default rules | Conservation, collateral valuation, liquidation, bad-debt and stress tests | Origination / servicing fees, subject to licensing |
| 23 | **Stable Assets & Reserve Management** | `synergy_usds`, `synergy_cashero`, `synergy_triangle_money_system` | Distinct liability classes, reserve proofs, redemption and liquidity management | Credential remediation, legal structure, independent reserve reconciliation, redemption stress and contract audit | Issuance / servicing fees |
| 24 | **Cross-Chain Messaging & Settlement** | `synergy_chain`, `synergy_metachain`, `synergy_ai_blockchain` | Authenticated cross-domain messages and replay-safe state transitions | Adversarial bridge tests, finality assumptions, relayer failure and recovery proofs | Message / settlement fees |
| 25 | **On-Chain Governance & Treasury Controls** | `synergy_ai_blockchain`, `synergy_chain`, `synergy_financial_os` | Proposal, delegated authority, timelock, budget controls and transparent execution | Sybil/capture analysis, quorum tests, timelock, emergency pause and ledger reconciliation | Governance tooling license |

### Division F — Cooperative & Synergistic Economy

| # | Capability | Candidate canonical anchors | Initial product boundary | First acceptance evidence | Revenue model |
|---:|---|---|---|---|---|
| 26 | **Mutual Credit & Multilateral Clearing** | `synergy_agentic_ai_economy`, `synergistic_economics`, `synergy_triangle_money_system` | Bounded credit limits, reciprocal obligations, netting and settlement | Double-entry conservation, exposure caps, default waterfall, dispute and liquidity stress tests | Clearing / membership fees |
| 27 | **Value Network & Contribution Accounting** | `synergistic_economics`, `synergy_ai_economic`, `synergy_agentic_ai_economy` | Typed graph of contributions, outputs, claims, ownership and externalities | No double counting, causal attribution limits, auditability and appeal workflow | Analytics / institutional license |
| 28 | **Cooperative Marketplace** | GAP; potential integration with `synergy_apps` and `synergy_ai_company` | Joint procurement, shared services, production matching and transparent payout rules | Participant identity, escrow/settlement, dispute process and unit-economics tests | Marketplace commission / SaaS |
| 29 | **Resource & Capacity Exchange** | GAP; compute capacity may connect to `synergy_computing_topology` | Match idle equipment, compute, storage, logistics and service capacity to demand | Resource attestation, availability, metering, SLA, dispute and settlement evidence | Usage fee / marketplace commission |
| 30 | **Economic Simulator & Policy Lab** | `synergistic_economics`, `synergy_ai_economic`, `synergy_agentic_ai_economy`, `synergy_search_engline` | Compare institutional and monetary mechanisms under common initial conditions | Historical calibration, frozen benchmarks, sensitivity, OOS scenarios, conservation and falsification report | Research license / consulting / institutional API |

## 5. Portfolio status: what is already present versus what is missing

The current repository landscape contains meaningful anchors for many capabilities, but the anchors have different maturity levels:

- `synergy_riskguard` README describes an Enterprise v2.0.0 product, 21 passing tests and local health/throughput smoke results. These are local software checks, not a production SLA or proof of trading alpha.
- `synergy_meta_api` README explicitly identifies V0.1 as a prototype, local read-only tools only, and lists authentication, tenant isolation, audit, quotas and secret-management work before public production.
- `synergy_ai_company` README labels the organization architecture STUB / concept.
- `synergy_metaverse` and `synergy_maps` require evidence-led revalidation; the 2026-11-20 atlas says the Maps main branch is README-only and the Metaverse inspected branch was a catalogue/research state, not a proven spatial runtime.
- `synergistic_economics` contains a broad research program and executable prototypes, but its own README does not claim empirical validity of the complete theory.
- `synergy_agentic_ai_economy` reports deterministic simulation benchmarks and explicitly separates internal GDP / transaction volume from HardNAV and external P&L. These remain simulation results, not deployed-market earnings.
- `synergy_meta_os` is defined as a runtime orchestrator, distinct from the architecture/governance root. Its README sets a local reproducible node milestone; it does not claim a fully qualified universal operating system.
- The 2026-11-20 registry records 39 contracts, 44 adapter edges and zero E2E-tested federation edges. Do not advertise these adapter edges as completed product integrations.

**Portfolio conclusion:** the immediate expansion opportunity is to productize and connect existing research and prototypes, while building genuinely missing business workflows. The portfolio should not create duplicate repositories for CEO AI, risk, quant, portfolio, economic simulation, memory or blockchain when an existing authority already owns that domain.

## 6. Critical blockers and release gates

The 2026-11-20 security blocker register records four unresolved P0 findings and one P1 finding. They must be treated as release blockers until externally remediated and independently verified:

- `synergy_usds`: deployer credential filename in the main tree; rotation/revocation and history remediation not verified.
- `synergy_cashero`: non-placeholder credential/private-key-like material was found in environment files; assume compromised and rotate/revoke externally.
- `synergy_turbo_linux`: private-key-like PuTTY file; determine validity, rotate if real, remove from tree/history.
- `synergy_ai_trade_terminal`: non-placeholder broker credential literals in source; revoke externally, review account activity and remove credentials.
- `synergy_hierarchical_cognitive_memory_architecture` (P1): authentication/authorization, symlink containment and cross-repository source namespace issues remain unresolved on the inspected feature branch.

Do not copy credential values into reports. Do not deploy affected components or promote them into a federation release until remediation evidence is attached. This document does not change blocker status.

### Universal maturity gates

| Gate | Name | Required evidence |
|---|---|---|
| G0 | Scope & ownership | Named owner, bounded context, data classification, rights/licensing review |
| G1 | Reproducible component | Pinned environment, clean install/run, deterministic tests and negative tests |
| G2 | Contract conformance | Versioned schema, compatibility tests, authz, idempotency, provenance and failure semantics |
| G3 | End-to-end integration | Exact commit SHAs, executable cross-repo path, trace IDs, CI with visible runner steps and retained artifacts |
| G4 | Controlled deployment | Threat model, secrets management, observability, rollback, SLO, incident response and human approvals |
| G5 | Commercial validation | Paying customers, renewal/retention, unit economics, support burden and lawful operating model |

A capability cannot skip a gate because another repository has a green test. CI that fails before runner allocation is **not** a test pass.

## 7. Recommended execution sequence

### Wave 0 — Safety and evidence (immediate prerequisite)
1. Remediate the four P0 and one P1 security findings.
2. Reconcile the 92-repository inventory with the 76-record interface registry and the current contract register.
3. Enrich the highest-value repository passports: exact main SHA, active branch/PR lineage, tests actually executed, release artifacts and runtime status.
4. Re-establish CI runner execution for central validators and priority repositories.
5. Keep merge-ready count at zero until exact-head checks and dependency stacks are proven.

### Wave 1 — Revenue-oriented productization
1. RiskGuard: convert the existing technical pilot surface into a reproducible customer pilot with strict limits and no implied return guarantee.
2. Quant Lab + MIDAS: standardize research evidence and portfolio decision contracts; preserve independent risk veto.
3. Financial OS + Treasury: establish ledger-backed cash forecasting and reconciliation.
4. Meta API: finish authentication, tenant isolation, scopes, secret vault, audit, quotas and egress controls before any external execution.
5. Lead discovery / CRM: keep outbound actions approval-gated; test provenance, deduplication and consent.

### Wave 2 — Economic and agent integration
1. Specify the common identity, agent capability and mission lifecycle contracts.
2. Separate knowledge memory, engineering evidence archive and mission ledger; connect through explicit adapters, not a monolithic store.
3. Connect the Agentic AI Economy to the canonical accounting/event model without treating simulated internal volume as external revenue.
4. Build mutual-credit and cooperative marketplace as sandboxed research/pilot modules with bounded exposure and dispute processes.

### Wave 3 — Financial network infrastructure
1. DEX/liquidity router only after smart-contract audit and reproducible fork testing.
2. Credit and stable-asset modules only after legal, reserve, redemption, default and liquidity analysis.
3. Cross-chain messaging only after threat model, finality model, replay protection and incident recovery.
4. On-chain governance only after authority separation, timelock and emergency controls.

### Wave 4 — Human and enterprise expansion
1. Build Human OS on explicit user consent and export/deletion controls.
2. Add procurement and supply-chain workflows through standard connectors and approval gates.
3. Add education, health and legal domains only with domain-specific safety, privacy and professional review.
4. Add resource exchange only after metering, identity, SLA, dispute and settlement evidence.

## 8. Cross-domain contract backlog

The following are candidate contract families to specify and test. They are not claimed to exist merely because names are listed here.

1. `synergy.identity.credential/v1` — identity and verifiable credential lifecycle.
2. `synergy.agent.capability-grant/v1` — scoped, revocable agent permissions.
3. `synergy.agent.mission/v1` — mission state, lease, fencing, idempotency and approval.
4. `synergy.business.workflow/v1` — business process task and approval.
5. `synergy.procurement.quote/v1` — supplier quote provenance and normalized terms.
6. `synergy.resource.capacity/v1` — resource offer, reservation, metering and SLA.
7. `synergy.investment.proposal/v1` — investment thesis, evidence, constraints and approvals.
8. `synergy.portfolio.intent/v1` — portfolio target and permitted rebalance intent.
9. `synergy.risk.decision/v1` — independent allow/resize/deny/kill result.
10. `synergy.trading.execution-result/v1` — venue execution facts and fees.
11. `synergy.accounting.journal-entry/v1` — balanced, idempotent financial recognition.
12. `synergy.payment.settlement-evidence/v1` — external payment and settlement proof.
13. `synergy.credit.obligation/v1` — debtor, creditor, amount, maturity, collateral and dispute state.
14. `synergy.asset.rights/v1` — legal right, issuer, custodian, jurisdiction and redemption.
15. `synergy.chain.commitment/v1` — chain event reference, finality and proof metadata.
16. `synergy.economy.contribution/v1` — measured contribution with causal uncertainty and appeal.
17. `synergy.economy.simulation-run/v1` — scenario, parameters, seed, code/data hashes and metrics.
18. `synergy.evidence.bundle/v1` — reproducible test, benchmark or deployment evidence.

Each contract must define owner, producer, consumer, schema, authentication, authorization, idempotency, ordering, retry, expiry, error model, privacy classification and conformance tests.

## 9. Portfolio KPIs

Do not use repository count, LOC, gross TVL, internal transaction volume or number of agents as primary success metrics.

### Engineering
- percentage of repositories with current owner, exact main SHA and deep passport;
- percentage of contracts with executable conformance tests;
- number of E2E-tested edges with retained evidence;
- critical/high security findings open and age;
- reproducible build/test success rate;
- mean time to detect and recover from failed deployment.

### Product
- time-to-first-value;
- active paying organizations and users;
- activation and 30/90-day retention;
- support hours per customer;
- gross margin and hosting/inference cost per workflow;
- customer-approved workflow completion rate.

### Finance and markets
- external realized P&L separated from simulation and internal transfers;
- fees, slippage, funding, borrow, gas and execution costs;
- max drawdown, tail loss and exposure concentration;
- reconciliation breaks and settlement failures;
- customer assets and protocol liabilities reported separately.

### Cooperative economy
- verified useful output;
- productive capacity utilization;
- net value added with intermediate inputs removed;
- credit exposure, defaults and recovery;
- liquidity coverage and maturity mismatch;
- distribution outcomes and concentration;
- externalities and resource constraints.

## 10. Repository creation policy

A new repository is justified only if all conditions are met:

1. The capability is not already owned by a canonical repository.
2. It has an independent domain model and state authority.
3. It needs a distinct release/deployment lifecycle or security boundary.
4. It has a named maintainer and a reproducible acceptance plan.
5. Its contracts with existing components are specified before implementation.

Otherwise, implement as a bounded module in the current owner repository and register it in the atlas. This avoids repository inflation and duplicated authority.

## 11. Open decisions for the next implementation pass

These decisions should be resolved from source and current branch evidence, not by assumption:

- Which repository owns the canonical identity and delegated-agent authorization service?
- Which repository owns the mission lifecycle after reconciling Autopilot and Long-Term Harness?
- Which repository owns canonical accounting journal entries and settlement recognition?
- Which existing AMM/DEX repository is the canonical implementation versus research/simulation?
- Which of the 30 capabilities has a real customer pilot, and what artifact proves it?
- Which existing CI failures are infrastructure-only and which are code/test failures?
- Which new capability is sufficiently independent to warrant a new repository?

## 12. Definition of done for SYNERGY 2X v1

SYNERGY 2X v1 is complete only when:

- all 30 capability domains have a canonical owner or an explicit GAP owner;
- each mapped repository has a current evidence passport;
- no architectural edge is represented as runtime integration without proof;
- critical security blockers are closed with external remediation evidence;
- priority contracts have schema and conformance tests;
- at least one full E2E workflow per launch division passes on exact commit SHAs;
- commercial claims are tied to paying-customer evidence;
- all research/simulation results remain clearly separated from deployed production outcomes.

**Final principle:** expand the capabilities of the ecosystem, not the number of disconnected repositories. The first multiplier is reliable integration, verified security and repeatable customer value.
