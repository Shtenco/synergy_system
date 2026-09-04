# SYNERGY Artifact / Evidence Envelope v1

Date: 2026-08-29

Status: **PROVENANCE CONTRACT READY — NOT A LIVE/PRODUCTION CERTIFICATE**

## Purpose

`synergy.artifact-evidence-envelope/v1` is the common cross-repository identity/provenance wrapper for the SYNERGY federation. It lets Financial OS, MetaPay, blockchain, NEXUS, MIDAS, client apps and later all other repositories exchange artifact identities without collapsing their authority boundaries.

The envelope answers:

- what artifact identity is being referenced;
- which repository/commit produced or sourced it;
- which domain owns the underlying claim;
- in which environment it was observed;
- which parent evidence roots it depends on;
- which source verifier root, if any, is referenced;
- what canonical envelope digest binds those fields.

It does **not** answer whether an arbitrary source claim is true. Truth of the underlying source artifact remains the responsibility of that source domain and its independent verifier/evidence policy.

## Non-authority invariant

Every envelope is permanently:

- `authority_scope = IDENTITY_AND_PROVENANCE_ONLY`
- `evidence_status = PROVENANCE_ENVELOPE_ONLY`

and all operational authority fields are exactly `NONE`:

- financial
- payment
- accounting
- execution
- signing
- blockchain submission
- production deployment
- merge

Therefore an envelope can carry provenance for a production or live-external artifact, but the envelope itself cannot authorize or certify the production/live action.

## Integrity rules

The runtime verifier is fail-closed and requires:

1. exact top-level field set;
2. exact metadata field set;
3. lowercase SHA-256 artifact/envelope identities;
4. exact lowercase Git SHA-1 source commit identity;
5. canonical UTC `Z` timestamp;
6. sorted unique parent digests;
7. supported authority-domain/environment vocabulary;
8. no authority escalation;
9. canonical SHA-256 over the envelope body excluding `envelope_digest`.

A fresh rehash does not permit hidden fields, self-promotion, or authority escalation.

## Source status semantics

`source_status_text` is deliberately provenance text, not an authorization token. The envelope may transport the exact status emitted by a source system, but does not reinterpret or independently certify that status.

For example, a source string containing `LIVE_VERIFIED` still leaves the envelope itself at `PROVENANCE_ENVELOPE_ONLY` with every operational authority equal to `NONE`.

If the receiving workflow requires a verified source claim, it must separately verify the referenced source artifact/verifier according to that domain's policy.

## Six-domain conformance set

The first conformance generation covers:

1. `Shtenco/synergy_financial_os` — AvailableCapacity lineage;
2. `Shtenco/synergy_pay_system` — settlement/reversal lineage;
3. `Shtenco/synergy_ai_blockchain` — local restart/persistence evidence;
4. `Shtenco/agi_nexus` — benchmark record provenance;
5. `Shtenco/midas_ai` — research/shadow record provenance;
6. `Shtenco/synergy_app` — client release metadata provenance.

These are **conformance examples**, not proof that all referenced artifacts are live, production, audited or externally executed.

## Adversarial contract

`tests/test_artifact_evidence_envelope_v1.py` verifies positive examples and fresh-rehash attacks including:

- hidden top-level live claim;
- hidden metadata authority;
- evidence-status self-promotion;
- authority-scope escalation;
- each operational authority field escalation;
- unsorted/duplicate parent roots;
- noncanonical UTC timestamp;
- repository namespace escape;
- malformed source/artifact/verifier digests;
- unsupported environment/domain;
- production/live environment without authority inheritance.

## Federation integration

This contract is intended to become the common evidence envelope underneath the 42-repository Federation v2 roadmap. Adoption by another repository must be additive and must not silently rewrite that repository's historical evidence format.

## Promotion policy

This generation grants no merge or production authority. Canonical adoption remains human-maintainer controlled. A GitHub workflow file is only a CI definition; no CI PASS is claimed unless an executed run with usable step/result evidence is separately observed.
