# SYNERGY Federation Trust Registry v1

`Shtenco/synergy_system` owns federation governance metadata. `Shtenco/shttps` implements PQ identities, registry signing/verification, trust-store derivation, rotation, revocation and RPC enforcement. Private keys are runtime secrets and are never governance-repository content.

## Trust chain

```text
federation root identity (ML-DSA-87 AND SLH-DSA-SHAKE-256s)
        |
        +-> public federation root document (pinned out-of-band)
        |
        +-> signed federation registry sequence N
                 |
                 +-> exact 51 capability-repository entries
                 +-> separate control-plane principals
                 +-> active/retiring/revoked node public identities
                 +-> roles/risk/integration metadata
                 +-> caller RPC ACLs
                 +-> previous_registry_hash
```

A registry is accepted only when every required root signature verifies, the registry is inside its validity window, the monotonic sequence does not roll back, and the previous-hash chain matches the locally accepted state.

## Provisioning

Production-candidate provisioning is performed by `shttps-federation` with the pinned OQS provider. `root-init` writes the root private identity to the configured protected secret path and a separate public root file. `provision-all` consumes `config/federation_trust_source_v1.json`, creates an independent PQ node identity for all 51 capability repositories and any explicit control-plane principals, writes private identities only to the configured secret directory, and emits a signed public registry.

The current `liboqs-python` provider exports secret-key bytes. Therefore the current automated profile is **encrypted file-secret storage on a protected signing node**, not a non-exportable HSM profile and not a cold/offline root. A future HSM/delegated-signer provider must remove the root private identity from routine registry maintenance.

High-impact repositories (`financial`, `blockchain`, plus `synergy_system`) receive ML-DSA-87 **AND** SLH-DSA-SHAKE-256s node identities. Other repositories and the Auto-Company control principal receive ML-DSA-87 by default. This identity policy is separate from payment, treasury, validator or blockchain keys.

## Rotation, renewal and revocation

`rotate` creates a new independent key generation. The previous active node becomes `retiring` for a bounded grace interval, so clients can accept old and new IDs while preferring the newest active generation. After the grace interval the old node disappears from derived trust automatically.

Registry lifetime and node-key lifetime are independent. Automatic maintenance renews a signed registry before its own expiry even when no node key is due, preserving monotonic sequence and the `previous_registry_hash` chain.

Batched `rotate-due` is crash-safe: generation and `.next` private files are created first, Registry N+1 is signed and atomically published next, and only then are pending private identities atomically promoted to stable paths. Either crash boundary leaves a registry/private-key combination that still authenticates.

`revoke` marks a node `revoked`; revoked IDs are omitted from derived trust immediately. Every rotation/renewal/revocation that changes the registry produces `sequence+1` and binds `previous_registry_hash` to the prior signed registry.

Federation root rotation is separately cross-signed by the old MAX root before a new public root can be trusted.

## Caller capabilities

Registration does not grant execution. All 51 capability repositories start with `capability_policy=DENY` and an empty caller RPC list. Ownership of an endpoint never grants the repository the right to call that endpoint.

`synergy_ai_company` is represented separately as a control-plane principal. Its initial allowlist contains only the already implemented Auto-Company -> Autopilot and Auto-Company -> NEXUS RPC routes. New callers or routes require an explicit governance update and a newly signed registry sequence.

Transport authorization is still not domain authorization: a permitted SHTTPS RPC route cannot bypass Autopilot approvals, NEXUS execution_authority=NONE, financial policy, payment signing, accounting or blockchain controls.

## Deployment rule

A service must be configured with:

- its private identity secret path;
- the signed federation registry;
- the pinned public federation root;
- its canonical repository/principal name;
- local accepted-registry state for rollback protection.

SHTTPS derives peer trust and caller ACLs from the signed registry. Manual peer trust files are legacy migration mode only and require an explicit override.
