# SYNERGY Federation V4/V5 Design

**Date:** 2026-09-17  
**Architecture root:** `Shtenco/synergy_system`  
**Scope:** all repositories currently accessible under `Shtenco`; observed inventory was 58 at design approval and is 59 as of 2026-09-18 after `synergy_agi_trader` appeared  
**Status:** approved design specification; implementation pending  

## 1. Goal

Turn the current collection of repositories, trust metadata, capability contracts and domain schemas into one governed federation in which repository existence grants no runtime authority.

The core invariant is:

```text
GitHub repository
       !=
Federation principal
       !=
trusted node
       !=
capability
       !=
authority
```

The only valid promotion chain is:

```text
Repository
  -> Repository Registry
  -> Lifecycle Status
  -> Capability Declaration
  -> Authority Policy
  -> Trust Eligibility
  -> PQ Identity
  -> SHTTPS Authentication
  -> Caller ACL
  -> Capability Validation
  -> Canonical Object
  -> Evidence
```

No new repository is created by this migration.

## 2. Source of truth

`synergy_system` becomes the sole governance source for repository classification, authority, trust eligibility, capability ownership and canonical cross-domain contracts.

The canonical source file will be:

```text
config/repository_catalog_v5.json
```

All derived federation files are generated from this catalog. Existing hand-maintained `repository_federation_v1.yaml` and `federation_trust_source_v1.json` become migration inputs only and must not remain independent authorities after V5 cutover.

Repository count is always computed from the catalog. No code may hard-code `51`, `52`, `58`, or any later repository count as a governance invariant.

## 3. Repository lifecycle vocabulary

Every repository has exactly one lifecycle status from this closed set:

```text
CANONICAL
CANDIDATE
R&D
LEGACY
ARCHIVE
```

The lifecycle status is distinct from system kind. System kind describes what a repository is, for example:

```text
DOMAIN_SERVICE
CONTROL_PLANE
INFRASTRUCTURE
CLIENT
PRESENTATION
RESEARCH
PROVENANCE
```

A `CANONICAL` presentation repository still has no financial or execution authority unless explicitly granted by the authority map.

### CANONICAL

Current authoritative implementation or governance owner for a responsibility. It may become trust-enabled only if verification and security gates pass.

### CANDIDATE

Intended successor or production candidate. It may use staging/test trust identities, but receives no production authority merely because of candidate status.

### R&D

Research and experimentation. It may produce evidence, strategies, technology candidates and reproducible results. It cannot self-authorize payment, accounting, treasury, settlement or production execution.

### LEGACY

Historical/provenance implementation retained for audit or migration. Default production caller authority is `NONE`. It cannot receive a production SHTTPS identity unless explicitly promoted through a catalog change reviewed under the same governance rules as any other authority change.

### ARCHIVE

Retained only for history, redirect or provenance. It is excluded from runtime federation and cannot receive trust identity or capability authority.

## 4. Repository catalog schema

Each repository entry must contain, at minimum:

```text
name
github_id
repo_url
default_branch
visibility
lifecycle_status
system_kind
domain
role
risk_class
federation_membership
trust_enabled
authority
capabilities_provided
capabilities_consumed
allowed_exchange_objects
canonical_successor
provenance_sources
verification
```

`authority` is explicit and machine-readable. It must represent at least:

```text
execution
financial
accounting
payment
settlement
blockchain_submission
code_write
external_side_effect
```

Absence of an authority grant means `NONE`.

## 5. One authority per fact

The federation preserves one canonical authority for each material fact class.

At minimum:

```text
architecture governance -> synergy_system
canonical accounting / HardNAV -> synergy_financial_os
payment routing / settlement -> synergy_pay_system
trading intelligence -> midas_ai
reasoning / memory -> agi_nexus
bounded business execution -> agi_autopilot
business orchestration -> synergy_ai_company
real-economy project model -> synergy_eurasian
science workflow -> nexus_science_agent
secure session / federation cryptographic enforcement -> shttps
network relay / transport -> synergynet
node orchestration -> synergy_meta_os
host capability substrate -> turbo_linux
trust commitments -> synergy_ai_blockchain
lossless compression -> ai_compress
requirement semantics -> ai_language
```

Two `CANONICAL` repositories may not own the same exclusive authority. CI must fail if an exclusive authority has zero or more than one canonical owner.

## 6. Federation membership and trust eligibility

The live GitHub inventory is not identical to the runtime principal set. Repository count is intentionally dynamic and is derived from the canonical catalog.

The model is:

```text
all repositories
   -> classification
   -> federation membership decision
   -> trust eligibility decision
   -> SHTTPS principal/node material only for eligible entries
```

`ARCHIVE` repositories are never trust-enabled.

`LEGACY` repositories are trust-disabled by default.

`R&D` repositories are read/evidence-oriented by default and cannot gain high-impact economic authority through capability declaration alone.

Infrastructure repositories such as `shttps` may be governance/trust infrastructure without acting as ordinary business callers.

## 7. Deterministic generated artifacts

The V5 generator must derive the following from the canonical catalog:

```text
generated/repository_registry_v5.json
generated/authority_map_v5.json
generated/capability_registry_v2.json
generated/federation_trust_source_v5.json
generated/exchange_object_registry_v1.json
generated/federation_graph_v5.json
generated/FEDERATION_STATUS_MATRIX.md
```

Generated artifacts must be deterministic for identical source input.

Every generated artifact must carry a digest that binds it to the exact canonical catalog version/digest.

CI must detect manual drift by regenerating artifacts and comparing byte-for-byte or canonical-JSON-equivalent output.

## 8. Capability Contract V2

The federation upgrades the existing `synergy.capability.v1` envelope to:

```text
synergy.capability.v2
```

A request must include:

```text
protocol
request_id
source_principal
target_principal
capability
input.object_type
input.schema_version
input.payload
constraints
approval_context
idempotency_key
trace_id
```

A result must include:

```text
protocol
request_id
provider
capability
status
result_objects
evidence
usage
cost
trace_id
authority_statement
```

Closed result statuses:

```text
ACCEPTED
REJECTED
RUNNING
COMPLETED
FAILED
```

Capabilities are deny-by-default. A repository may not call a capability because it exists in GitHub, exists on disk, or appears in a task payload.

No capability contract grants arbitrary shell access. Credentials are never accepted inside capability payloads.

## 9. Capability registry

Capabilities use stable namespaces such as:

```text
research.*
science.*
market.*
trading.*
finance.*
accounting.*
payment.*
settlement.*
business.*
engineering.*
network.*
trust.*
compression.*
application.*
```

Every exclusive capability has one canonical owner.

Examples:

```text
accounting.recognize_external_profit -> synergy_financial_os
payment.route -> synergy_pay_system
trading.propose_portfolio -> midas_ai
science.build_evidence_package -> nexus_science_agent
business.execute_approved_task -> agi_autopilot
```

R&D repositories can provide candidate/research capabilities but cannot override exclusive canonical capabilities.

## 10. Canonical exchange objects

Federation V5 freezes the following cross-domain object vocabulary:

```text
DemandSignal
ResourceState
TechnologyCandidate
ProjectProposal
CapitalAuthorization
PaymentIntent
SettlementReceipt
EvidencePackage
AccountingSnapshot
```

Existing compatible schemas are migrated with provenance rather than silently rewritten.

Canonical semantic owners:

```text
DemandSignal -> federation contract, producer-dependent
ResourceState -> federation contract, producer-dependent
TechnologyCandidate -> science / research producers under federation contract
ProjectProposal -> synergy_eurasian domain contract
CapitalAuthorization -> synergy_financial_os authority boundary
PaymentIntent -> financial/policy authorization boundary consumed by synergy_pay_system
SettlementReceipt -> synergy_pay_system
EvidencePackage -> evidence-producing domains under federation contract
AccountingSnapshot -> synergy_financial_os
```

`synergy_system` owns versioning and federation-level compatibility rules, not the domain truth inside accounting, settlement or research artifacts.

## 11. Required economic authority barriers

The following are forbidden independent of repository status:

```text
NEXUS cannot create AccountingSnapshot as accounting truth.
MIDAS cannot create CapitalAuthorization.
MetaPay cannot recognize revenue or HardNAV.
Messenger/client applications cannot create accounting truth or expose generic wallet signing authority.
Blockchain cannot redefine SettlementReceipt or AccountingSnapshot.
R&D token/AMM systems cannot classify internal mark-to-market movement as external profit.
```

Only reconciled external economic evidence may reach canonical accounting according to Financial OS policy.

## 12. SHTTPS integration

The existing SHTTPS registry remains the cryptographic enforcement layer. V5 governance metadata is generated into the trust source and then signed through the existing Root / delegated Registry Signer lifecycle.

The trust-source generation path becomes:

```text
repository_catalog_v5
  -> deterministic governance projection
  -> federation_trust_source_v5
  -> Federation Root / certified Registry Signer
  -> signed registry sequence N
  -> SHTTPS runtime verification
```

SHTTPS must receive, directly or through governance projection, enough metadata to enforce:

```text
repository lifecycle status
system kind
risk class
authority class
capability ownership / allowlist
exchange-object permissions
catalog digest
```

Cryptographic registry sequence, previous-hash chaining, signer revocation, node lifecycle and anti-rollback rules remain independent from repository lifecycle classification.

## 13. Caller ACL policy

Default policy remains `DENY`.

A caller route is legal only if all of the following hold:

```text
source principal is trusted and active
target principal is trusted and active
source lifecycle permits runtime calls
requested capability exists
source is allowed to consume the capability
target is the canonical/allowed provider
RPC route is allowlisted
input canonical object type is allowed
required approval context is present
risk constraints are satisfied
```

Failure of any condition rejects the call.

## 14. Canonical successor and provenance

Legacy/R&D lineage is represented explicitly instead of being inferred from names.

Examples include historical MIDAS implementations pointing to `midas_ai`, and historical print-money implementations pointing to `synergy_graph_print_money` where appropriate.

`canonical_successor` graphs must be acyclic.

Archiving a repository does not delete provenance. Promotion to `CANONICAL` requires an explicit catalog change and verification evidence; it is never automatic.

## 15. Verification model

Repository verification is separate from lifecycle status.

The catalog must support machine-readable gates such as:

```text
IMPLEMENTED
TESTS_PRESENT
LOCAL_RUNNER_EXECUTED
HOSTED_CI_EXECUTED
INTEGRATION_VERIFIED
SECURITY_REVIEWED
EXTERNAL_AUDIT
PRODUCTION_READY
```

A `CANONICAL` repository is not automatically `PRODUCTION_READY`.

A `CANDIDATE` repository may be technically stronger than a current canonical repository but still lacks authority until governance promotes it.

## 16. CI invariants

CI must fail when any of these invariants is violated:

```text
catalog contains duplicate GitHub repository IDs or names
repository inventory and catalog diverge without an explicit reviewed change
repository lacks lifecycle status
lifecycle status is outside CANONICAL/CANDIDATE/R&D/LEGACY/ARCHIVE
exclusive authority has != 1 canonical owner
ARCHIVE is trust-enabled
LEGACY has production caller authority without explicit exception
R&D has canonical accounting/payment/treasury authority
presentation has economic authority
canonical-successor graph has a cycle
capability has ambiguous canonical ownership
canonical exchange object has ambiguous schema/version owner
generated artifact differs from deterministic regeneration
trust-source catalog digest differs from canonical catalog digest
repository count is hard-coded instead of derived
```

Regression gates must preserve the currently approved Auto-Company routes to Autopilot and NEXUS unless a separate governance change intentionally modifies them.

## 17. Migration phases

### Phase V4-A — Catalog normalization

Create the full live-inventory canonical catalog, normalize lifecycle statuses and separate lifecycle from system kind.

### Phase V4-B — Authority and capability model

Create the machine-readable exclusive authority map, capability ownership model and consumer policy.

### Phase V4-C — Exchange object registry

Adopt the existing compatible schemas with provenance and add the missing canonical schemas under correct domain ownership boundaries.

### Phase V5-A — Deterministic generator

Generate repository registry, authority map, capability registry, exchange registry, trust source, graph and status documentation from the catalog.

### Phase V5-B — SHTTPS governance projection

Bind generated governance metadata and catalog digest into the signed trust path without weakening existing Root/delegated-signer anti-rollback guarantees.

### Phase V5-C — Runtime migrations

Migrate Auto-Company, Autopilot and NEXUS first, preserving their current route allowlist. Then migrate other canonical services, clients and approved R&D providers.

### Phase V5-D — Legacy restriction

Remove runtime trust from legacy/archive repositories unless an explicit governance exception exists. Preserve source and provenance without granting authority.

## 18. Non-goals

This migration does not:

- merge repositories into a monorepo;
- create new repositories;
- merge existing open PRs automatically;
- fabricate production PQ identities or HSM keys;
- grant every repository a SHTTPS identity;
- declare R&D findings production-ready;
- make blockchain an accounting authority;
- replace domain-owned economic truth with `synergy_system` logic.

## 19. Merge gates

No V4/V5 implementation is merged until:

1. deterministic catalog validation passes;
2. generated artifacts reproduce exactly;
3. capability/authority negative tests pass;
4. existing Federation Trust Registry security tests remain green locally;
5. Auto-Company -> Autopilot/NEXUS regression tests pass;
6. hosted CI is classified from actual executed steps rather than repository-level conclusion alone;
7. no private keys, HSM PINs or production credentials are committed;
8. a human explicitly authorizes merge.

## 20. End state

The target federation guarantees that source-code presence and runtime authority are separated by multiple independently verifiable gates.

A repository becomes operational only through explicit catalog classification, capability ownership, authority policy, trust eligibility, authenticated SHTTPS identity, caller ACL and canonical-object validation.

This is the governance boundary that turns the live repository estate into one controlled distributed system rather than a set of mutually trusting programs.
