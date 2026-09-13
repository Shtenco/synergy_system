# SYNERGY Federation Trust Registry v1

`Shtenco/synergy_system` owns federation governance metadata. `Shtenco/shttps` implements PQ identities, registry signing/verification, trust-store derivation, rotation, revocation and RPC enforcement. Private keys are runtime secrets and are never governance-repository content.

## Trust chain

```text
offline federation root secret (ML-DSA-87 AND SLH-DSA-SHAKE-256s)
        |
        +-> public federation root document (pinned out-of-band)
        |
        +-> signed federation registry sequence N
                 |
                 +-> exact 51 repository metadata entries
                 +-> active/retiring/revoked node public identities
                 +-> per-repository roles/risk/integration metadata
                 +-> deny-by-default RPC allowlists
                 +-> previous_registry_hash
```

A registry is accepted only when every required root signature verifies, the registry is inside its validity window, the monotonic sequence does not roll back, and the previous-hash chain matches the locally accepted state.

## Provisioning

Production provisioning is performed by `shttps-federation` with a standards-conformant OQS provider. `root-init` writes the root private identity to a secret/HSM path and a separate public root file. `provision-all` consumes `config/federation_trust_source_v1.json`, creates one independent PQ node identity for every registered repository, writes the 51 private identities only to the configured secret directory, and emits a signed public registry.

High-impact repositories (`financial`, `blockchain`, plus `synergy_system`) receive ML-DSA-87 **AND** SLH-DSA-SHAKE-256s node identities. Other repositories receive ML-DSA-87 by default. This identity policy is separate from payment, treasury, validator or blockchain keys.

## Rotation and revocation

`rotate` creates a new independent key generation. The previous active node becomes `retiring` for a bounded grace interval, so clients can accept old and new IDs while preferring the newest active generation. After the grace interval the old node disappears from derived trust automatically.

`revoke` marks a node `revoked`; revoked IDs are omitted from derived trust immediately. Every rotation/revocation produces registry `sequence+1` and binds `previous_registry_hash` to the prior signed registry.

Federation root rotation is separately cross-signed by the old MAX root before a new public root can be trusted.

## Capabilities

Registration does not grant execution. `capability_policy=DENY` means the repository is known and can receive a PQ identity, but has no inbound federation RPC authority. An `ALLOWLIST` entry authorizes only exact versioned routes. The initial source permits only the already implemented Autopilot and NEXUS RPC contracts; all other repositories remain deny-by-default until their service contract exists and is reviewed.

## Deployment rule

A service must be configured with:

- its private identity secret path;
- the signed federation registry;
- the pinned public federation root;
- its canonical repository name;
- local accepted-registry state for rollback protection.

SHTTPS derives peer trust from the signed registry. Manual peer trust files are legacy migration mode only and require an explicit override.
