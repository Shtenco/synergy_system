# SYNERGY SYSTEM — Typed Contract / Authority / Graph Coverage Audit

**Snapshot:** 2026-11-20  
**Mode:** read-only structural audit of the current `main` registries. No registry or runtime code was modified.

## Scope and source objects

- `registry/SYNERGY_REPOSITORIES.json`: 92 current repository records.
- `registry/CONTRACT_REGISTRY.json`: 39 contract definitions.
- `registry/AUTHORITY_REGISTRY.json`: 20 authority keys.
- `registry/DEPENDENCY_GRAPH.json`: 136 graph edges.

## Findings

### 1. Authority vocabulary is incomplete

The 39 contracts use 38 distinct authority labels. **22 of those labels are absent** from the 20-key authority registry:

```text
adaptive_policy
agent_economy_simulation
bridge_solvency_telemetry
compression_benchmark
crypto_market_anomaly
cryptographic_research
financial_scenario_research
hardware_architecture_model
institutional_research
investment_committee
market_graph
market_making
market_perception
mobile_source_integrity
monetary_simulation
public_budget_provenance
quantum_reference_research
reasoning_benchmark_generation
relative_value_research
scientific_model_consistency
source_provenance_graph
superapp_source_surface
```

This is a schema/governance coverage gap. It does not prove the contract implementations are absent; it means their declared authority domains have no corresponding canonical authority entry.

### 2. Contract IDs are not consistently represented in the dependency graph

The graph has 22 `RUNTIME_CONTRACT` edges with 22 distinct contract IDs. **17 of 39 contract definitions have no matching RUNTIME_CONTRACT edge**:

```text
synergy.trading.portfolio-decision/v1
synergy.trading.validation-decision/v1
synergy.trading.risk-decision/v1
synergy.trading.execution-plan/v1
synergy.trading.execution-result/v1
synergy.settlement.evidence/v1
synergy.accounting.recognition/v1
synergy.trust.commitment/v1
synergy.ai.proposal/v1
synergy.science.evidence-package/v1
synergy.economy.project-proposal/v1
synergy.engineering.requirement-trace/v1
synergy.engineering.change-evidence/v1
synergy.runtime.node-manifest/v1
synergy.transport.evidence/v1
synergy.archive.evidence/v1
synergy.economy.funding-authorization/v1
```

The graph separately has 22 `CONTRACT_FLOW` edges, but these represent only 16 distinct contract IDs because several contracts are repeated across multiple consumers. **23 of 39 contract definitions have no matching CONTRACT_FLOW contract ID**. The same 23 are absent from `RUNTIME_DEPENDENCY` contract IDs. These are three distinct checks and must not be collapsed into one count.

### 3. Two producer references do not resolve in the current repository registry

| Contract | Producer reference in contract registry | Current registry candidate |
|---|---|---|
| `synergy.science.quantum-reference-control/v1` | `Shtenco/binary_quantum_theory` | `Shtenco/synergy_binary_quantum_theory` |
| `synergy.science.provenance-graph/v1` | `Shtenco/epstein_network` | `Shtenco/synergy_epstein_network` |

The legacy names are not present in the current 91-record repository registry. The proposed current names are candidates only; verify GitHub rename/redirect and historical provenance before editing authoritative producer references.

## Corrected status statement

The previous README wording that said “17 of 39 contract IDs without CONTRACT_FLOW edges” conflated edge types. The evidence supports this precise statement:

- 22/38 distinct contract authority labels are missing from `AUTHORITY_REGISTRY.json`.
- 17/39 contract IDs lack `RUNTIME_CONTRACT` edges.
- 23/39 contract IDs lack `CONTRACT_FLOW` edges.
- 23/39 contract IDs lack `RUNTIME_DEPENDENCY` contract IDs.
- 2 producer repository references do not resolve in the current 91-repository registry.

## Recommended remediation order

1. Resolve the two producer aliases using GitHub redirect/history evidence; do not infer a rename from a similar name alone.
2. Decide whether the 22 missing authority labels are valid independent domains or should map to existing canonical authorities. Add no authority by name-only copying.
3. Add or explicitly classify missing graph edges for all 39 contracts. Each edge must identify producer, consumer, direction, contract ID, lifecycle status and evidence.
4. Add a deterministic registry validator that fails on unknown authority labels, unresolved repository references, missing producer/consumer nodes, duplicate contract IDs with incompatible semantics, and inconsistent edge coverage.
5. Re-run structural validation and only then update the maturity status. No contract should be promoted to E2E_TESTED or DEPLOYED from registry presence alone.

## Evidence files

- `registry/CONTRACT_REGISTRY.json`
- `registry/AUTHORITY_REGISTRY.json`
- `registry/DEPENDENCY_GRAPH.json`
- `registry/SYNERGY_REPOSITORIES.json`


## Owner-inventory update — 2026-11-20

The owner registry now contains 92 repositories. The newly registered cognitive-memory repository is not one of the 39 existing contract definitions and is intentionally recorded as one uncontracted component in `INTEGRATION_GAPS.json`. This structural audit's contract and authority findings remain scoped to the 39 registered contracts; no new runtime edge is credited.
