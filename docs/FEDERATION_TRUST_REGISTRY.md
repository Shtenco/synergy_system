# SYNERGY Federation Trust Registry v2

`Shtenco/synergy_system` owns canonical federation governance metadata. `Shtenco/shttps` implements cryptographic identity, delegated registry signing/verification, trust derivation, rotation, revocation and RPC caller enforcement. Private keys never belong in the governance repository.

## Trust chain

```text
cold/offline Federation Root
ML-DSA-87 AND SLH-DSA-SHAKE-256s
        |
        +-> pinned public Federation Root
        |
        +-> Root-signed Registry Signer Certificate
        |      +-> non-exportable PKCS#11 ML-DSA-87 public identity
        |      +-> signer generation + validity interval
        |      +-> governance_hash
        |      +-> capability = federation.registry.lifecycle.sign
        |      +-> maximum delegated registry lifetime
        |
        +-> Root-signed Registry Signer Revocation State
               +-> monotonic sequence
               +-> previous_hash
               +-> revoked signer IDs

online PKCS#11 Registry Signer
        |
        +-> delegated signed Registry Sequence N
                 +-> exact 51 capability repositories
                 +-> separate control-plane principals
                 +-> active/retiring/revoked node identities
                 +-> immutable governance projection
                 +-> previous_registry_hash
```

The Federation Root private identity is not present on the online maintenance node. Routine Registry N -> N+1 signing is performed by the HSM-resident delegated signer.

## Governance boundary

The Root-signed signer certificate contains a `governance_hash` over the static federation governance surface:

- repository/control-principal names and repository URLs;
- domain, risk class, role and integration metadata;
- enabled status;
- caller `rpc_allow` lists;
- root id and repository count.

Node lifecycle records, registry sequence/timestamps and the previous-registry hash are deliberately outside this projection. Therefore the online delegated signer may rotate/revoke nodes and renew the registry, but it cannot add repositories, enable a caller, alter roles or expand RPC authorization. Any governance change requires the cold Root to issue a new signer certificate bound to the new governance hash.

## Signer revocation

Signer revocation is a separate Root-signed control plane. The revocation document has its own monotonic sequence and previous-hash chain. A service verifies the latest distributed revocation state together with every delegated registry.

A newer valid revocation state may invalidate an older registry signed by a now-compromised signer. The registry envelope records the revocation sequence/hash it was created against, but verification accepts a newer Root-signed revocation sequence while rejecting rollback, same-sequence equivocation and a signer ID that is now revoked.

This property allows emergency signer revocation without requiring a compromised HSM signer to cooperate.

## Initial provisioning

The production path is split into two ceremonies.

The cold/offline Root environment:

1. creates the Federation Root identity;
2. receives only the online HSM signer public descriptor;
3. signs the Registry Signer Certificate;
4. creates/signs the initial Registry Signer Revocation State.

The online HSM environment:

1. generates ML-DSA-87 in a PKCS#11 token with `SENSITIVE=true`, `EXTRACTABLE=false`, `PRIVATE=true`;
2. proves HSM/OQS interoperability using an immediate challenge signature;
3. imports only the public Root document, signer certificate and signer revocation state;
4. creates independent SHTTPS node identities for all 51 capability repositories plus the separate `synergy_ai_company` control principal;
5. emits delegated Registry Sequence 1 signed by the HSM signer.

The HSM Registry Signer private key is never exported. Node transport identities are still protected file secrets in this version; they are a separate key class and require a future per-service HSM provider if non-exportability is required for all 52 transport principals.

## Rotation, renewal and revocation

The online signer can perform lifecycle-only maintenance without Root access:

- renew the signed registry before expiry;
- rotate due node identities using active -> retiring -> expired lifecycle;
- revoke a compromised transport node;
- advance monotonic registry sequence and `previous_registry_hash`.

Rotation remains crash-safe: new generation/private `.next` material is created first, delegated Registry N+1 is signed and atomically published, and pending node identity material is promoted only after publication. The old node remains accepted as `retiring` during the bounded grace interval.

A compromised Registry Signer itself is different: its signer ID must be added to a new Root-signed revocation document offline. A replacement HSM key then receives a new Root-signed signer certificate/generation.

Federation Root rotation remains a separate cold-root operation cross-signed by the previous Root according to SHTTPS root-transition rules.

## Caller capabilities

Registration does not grant execution. All 51 capability repositories remain caller-deny with empty caller RPC lists. Endpoint ownership does not imply caller authority.

`synergy_ai_company` remains a separate control-plane principal. Its allowlist contains only the currently implemented five Autopilot and three NEXUS routes. The delegated signer cannot expand this list because it is covered by `governance_hash`.

Transport authorization is not domain authorization: SHTTPS cannot bypass Autopilot approval gates, NEXUS `execution_authority=NONE`, financial limits, payment signing, accounting or blockchain authority.

## Service deployment rule

Every production federation service using delegated Registry v2 must receive:

- its own transport private identity secret path;
- delegated `federation-registry.signed.json`;
- pinned public `federation-root.json`;
- Root-signed `registry-signer.revocations.json`;
- its canonical repository/control-principal name;
- local anti-rollback state.

The signer certificate is embedded in the delegated registry envelope; the independently distributed Root-signed revocation state is mandatory so services can invalidate a previously trusted signer. Manual trust files remain legacy migration mode only.
