# SYNERGY Federation V4/V5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Steps use test-first RED -> GREEN -> refactor.

**Goal:** Replace independent hand-maintained federation metadata with one canonical repository catalog and deterministic V5 projections into authority, capability, exchange-object and SHTTPS trust registries.

**Architecture:** `synergy_system` owns governance metadata and deterministic generation. `shttps` continues to own cryptographic enforcement. Domain truth stays with its canonical owner. GitHub repository existence grants no runtime authority.

**Tech Stack:** Python 3 standard library, JSON/JSON Schema, existing SHTTPS federation registry, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-17-federation-v4-v5-design.md`

## Global Constraints

- No new repositories.
- Repository count is derived from live catalog, never hard-coded.
- Lifecycle is exactly CANONICAL / CANDIDATE / R&D / LEGACY / ARCHIVE.
- Default caller/capability policy is DENY.
- ARCHIVE cannot be trusted; LEGACY is trust-disabled by default.
- R&D cannot own accounting/payment/settlement/treasury authority.
- Existing cold Root / delegated HSM signer / anti-rollback semantics remain unchanged.
- AutoCompany keeps only the approved five Autopilot + three NEXUS routes unless separately reviewed.
- No private keys, HSM PINs or production credentials.
- No merge without explicit human command.

---

### Task 1: Repository catalog
- Test first: `tests/test_repository_catalog_v5.py`.
- Create `config/repository_catalog_v5.json` and schema.
- Require unique GitHub name/id/url, closed lifecycle, explicit authority object, trust policy and provenance fields.
- Verify live catalog passes and newly discovered repositories default to no authority until classified.

### Task 2: Governance validator
- Test first: `tests/test_federation_v5_policy.py`.
- Create `scripts/federation_v5.py`.
- Enforce duplicate rejection, lifecycle rules, archive/legacy trust barriers, R&D and presentation economic barriers, exclusive-authority uniqueness and acyclic successors.
- Produce deterministic SHA3-256 catalog digest.

### Task 3: Capability Contract V2
- Test first: `tests/test_capability_registry_v2.py`.
- Add request/result JSON schemas and deterministic capability registry.
- Bind every exclusive capability to one canonical provider and explicit consumers.
- No arbitrary shell or credential-bearing task authorization.

### Task 4: Canonical exchange objects
- Test first: `tests/test_exchange_objects_v1.py`.
- Register exactly nine cross-domain objects.
- Preserve Eurasian provenance for existing schemas.
- Add missing federation contracts for CapitalAuthorization, PaymentIntent, SettlementReceipt and AccountingSnapshot.
- Domain truth remains with Financial OS / MetaPay / Eurasian owners.

### Task 5: Deterministic generator
- Test first: `tests/test_federation_v5_generation.py`.
- Create `scripts/generate_federation_v5.py`.
- Generate repository registry, authority map, capability registry, trust source, exchange registry, graph and status matrix.
- Same catalog must produce byte-identical outputs and one shared catalog digest.

### Task 6: SHTTPS trust projection
- Test first: `tests/test_federation_v5_trust_projection.py`.
- Only trust-enabled/federation-enabled principals are projected.
- AutoCompany stays a separate control principal with eight approved routes.
- Ordinary repository callers remain DENY.
- Do not change cryptographic signing/rotation semantics.

### Task 7: Drift gate
- Test first: `tests/test_federation_v5_regression.py`.
- Create `scripts/check_federation_v5.py`.
- Fail on generated drift, repository inventory drift, authority escalation, removed control route, successor cycle or catalog digest mismatch.
- Integrate with existing CI only if actual workflow runner steps execute.

### Task 8: Documentation and PR
- Document edit-source vs generated artifacts.
- Re-run full tests and drift check.
- Inspect diff for secrets/scope creep.
- Update PR #49 with actual V4/V5 evidence.
- Do not merge.

## Completion Gate

The implementation is complete only when the catalog validates, generation is deterministic, all derived JSON carries the same catalog digest, trust projection preserves deny-by-default and AutoCompany routes, negative authority tests pass, and no merge has occurred.
