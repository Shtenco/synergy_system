# SYNERGY Authority Boundaries

This document defines who is allowed to assert which kind of fact inside the SYNERGY federation.

The purpose is to prevent a system-of-systems failure mode in which several repositories independently become “sources of truth” for the same economic, security or execution fact.

## 1. Governing principle

```text
Architecture describes authority.
Domain owners produce facts.
Consumers verify facts.
No consumer silently promotes itself into the producer’s authority.
```

## 2. Exclusive authorities

### Architecture / federation

**Owner:** `Shtenco/synergy_system`

May define:
- repository map;
- dependency direction;
- architectural status vocabulary;
- authority ownership;
- cross-repository governance conventions.

May NOT:
- post ledger entries;
- execute payments;
- sign blockchain consensus state;
- make AI inference authoritative;
- modify another repository’s runtime state.

### Host / kernel

**Owner:** `Shtenco/synergy_turbo_linux`

May define host isolation/capability/kernel contracts.

May NOT infer economic authority from process privilege.

### P2P transport

**Owner:** `Shtenco/synergy_net`

May assert transport observations such as:
- content hash received;
- route/peer identity;
- chunk availability;
- transport timing;
- network cache state.

May NOT assert:
- accounting truth;
- revenue;
- payment settlement;
- blockchain economic finality merely because a packet was transported.

### Node runtime orchestration

**Owner:** `Shtenco/synergy_meta_os`

May start/stop/supervise services according to signed manifests and capabilities.

May NOT collapse distinct service authorities into one root process.

### Settlement

**Owner:** `Shtenco/synergy_pay_system`

May assert:
- PaymentIntent identity;
- route/execution status;
- settlement finality;
- reconciliation evidence;
- provider/rail readiness state.

May NOT assert:
- that settled money is revenue;
- HardNAV;
- distributable profit;
- capital authorization.

### Canonical accounting

**Owner:** `Shtenco/synergy_financial_os`

May assert:
- RevenueRecognition decisions;
- double-entry ReportingEntry facts;
- financial snapshots;
- HardNAV / LiquidNAV / EconomicNAV;
- accounting/period closes;
- restatement/replay results;
- solvency/liquidity/distribution capacity;
- accounting interpretation of settlement evidence.

May NOT execute an external payment directly merely because accounting capacity is positive.

### Household maturity / funding evidence

**Owner:** `Shtenco/synergy_matrix_sota`

May produce household/tranche/maturity facts.
Financial OS remains the consumer that decides how those facts affect consolidated liquidity/risk.

### Productive project facts

**Owner:** `Shtenco/synergy_eurasian`

May produce project proposals, physical constraints, cash-flow plans and evidence bundles.

May NOT promote a project to funded status by itself.

### Capital/distribution approval

Decision authority is represented in Financial OS artifacts but must come from explicit permitted governance such as human committee or multisig policy.

AI authority for direct approval remains `NONE` unless a future constitutional generation explicitly changes this rule with independently reviewed safeguards.

### NEXUS model authority

**Owner:** `Shtenco/synergy_agi_nexus`

May assert:
- model identity/version;
- inference result;
- benchmark artifact;
- training/evaluation provenance.

May NOT assert that its financial recommendation has been authorized or executed.

### Scientific research orchestration

**Owner:** `Shtenco/synergy_nexus_science_agent`

May produce:
- evidence graphs;
- search results;
- hypotheses;
- contradiction/falsification reports;
- reproducible research packages.

May NOT relabel simulation or synthesis as experimental scientific confirmation.

### MIDAS trading intelligence

**Owner:** `Shtenco/synergy_midas_ai`

May produce bounded trading/portfolio decisions under its risk constitution.

Only reconciled external results may be handed to Financial OS for accounting.

### Blockchain trust

**Owner:** `Shtenco/synergy_ai_blockchain`

May assert:
- commitment identity;
- typed payload hash;
- blockchain state/finality under the chain’s consensus rules;
- cryptographic provenance.

May NOT derive accounting meaning that was not present in the committed authoritative payload.

### Requirements semantics

**Owner:** `Shtenco/synergy_ai_language`

May assert requirement-registry identity and requirement/change/test trace relationships.

### Engineering evidence

**Owner:** `Shtenco/synergy_ai_coder`

May produce engineering change/evidence/review artifacts.

`REVIEWABLE` does not equal production deployment permission.

### Compression / archive identity

**Owner:** `Shtenco/synegy_ai_compress`

May assert codec/archive/hash/round-trip facts.

Compression ratio or archive presence does not confer authority over the archived domain.

### Presentation

Owners include:
- `Shtenco/synergy_chain`;
- `Shtenco/synergy_chain.github.io`;
- `Shtenco/sinergy_super_app`;
- public showcase repositories.

Presentation may verify and display authoritative artifacts.
Presentation does not create those facts.

## 3. Canonical economic chain

```text
External reality
  ↓
MetaPay settlement evidence
  ↓
Financial OS revenue recognition
  ↓
Financial OS double entry
  ↓
Accounting close / snapshot
  ↓
Policy and capacity
  ↓
Human/multisig authorization
  ↓
MetaPay execution
  ↓
new settlement evidence
  ↓
new accounting state
  ↓
Blockchain commitment
  ↓
read-only presentation
```

## 4. Forbidden shortcuts

The following direct transitions are architectural violations:

```text
AI recommendation        → payment
project screening        → payment
settlement receipt       → revenue
revenue recognition      → cash transfer
positive HardNAV         → automatic payout
positive LCR             → automatic payout
blockchain commitment    → accounting truth
portal button             → treasury authority
P2P transport success     → blockchain/economic finality
trading backtest          → Financial OS realized P&L
scientific simulation     → experimental confirmation
```

## 5. New repository rule

A new repository should be created only when all are true:

1. it owns a responsibility not cleanly owned elsewhere;
2. its authority can be named precisely;
3. its inputs/outputs can be represented by explicit contracts;
4. it does not require deleting or rewriting historical repositories;
5. it reduces coupling rather than merely adding another abstraction layer.

## 6. Versioning rule

Older generations remain valid provenance unless explicitly proven corrupt.
A newer version may supersede an older version for new production artifacts without deleting old bytes.

Use:

```text
v1 → v2 → v3
```

not:

```text
v1 → silently mutate v1
```

## 7. Security rule

Authority must be supported by technical enforcement:

- least privilege;
- capability boundaries;
- separate signing identities;
- HSM/KMS/MPC for high-value keys;
- signed manifests;
- idempotency / replay prevention;
- domain-separated hashes;
- exact schema/version binding;
- fail-closed stale-state checks;
- independent consumer verification.
