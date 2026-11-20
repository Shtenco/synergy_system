# Federation production deployment — cold Root + delegated PKCS#11 signer

This runbook deploys the SYNERGY Federation Trust Registry with a **cold/offline Federation Root** and a separate **non-exportable PKCS#11 ML-DSA-87 Registry Signer**. Routine online maintenance does not read or possess the Federation Root private key.

This remains a production-candidate implementation rather than a claim of completed third-party cryptographic certification. The transport layer uses OQS/liboqs and the online registry signer uses the token's PKCS#11 implementation; both must pass the supplied interop/preflight gates.

## Trust split

```text
offline/cold Federation Root
ML-DSA-87 AND SLH-DSA-SHAKE-256s
        |
        +-- signs Registry Signer Certificate
        |      signer public key: ML-DSA-87
        |      governance_hash: pinned
        |      capability: federation.registry.lifecycle.sign only
        |      bounded not_before/not_after
        |      bounded max registry lifetime
        |
        +-- signs Registry Signer Revocation State
               monotonic sequence + previous hash

online protected signing node
PKCS#11 token / HSM
non-exportable ML-DSA-87 signer private key
        |
        +-- Registry Sequence N -> N+1
        +-- node active/retiring/revoked lifecycle
        +-- registry renewal
        +-- cannot alter repositories, roles or rpc_allow
```

A compromised online signer therefore does not gain governance authority. `governance_hash` binds the signer certificate to the static federation policy. Changing repository membership, roles, enabled flags, integration metadata or caller ACLs requires a new certificate signed by the offline Root.

## Pinned software substrate

- liboqs `0.16.0`, commit `5a1a854b0dc9f2141bdc771c555ee60c37950183`
- liboqs-python `0.16.0`, commit `c6378cd5c8db74c0adf34ddcfbb96ee9c99f8061`
- python-pkcs11 `0.10.0`
- SHTTPS delegated-signing lineage pinned by `scripts/install_synergy_federation_stack.sh`
- ai_compress commit `551fae36eacb5713aa503fc9da2fbc44fe8f2e84`

Preflight requires ML-KEM-1024, ML-DSA-87, SLH-DSA-SHAKE-256s, X25519 hybrid mode, SGH1, python-pkcs11 0.10.0 and the PKCS#11 ML-DSA mechanisms.

## 1. Offline Root ceremony

Run this on an isolated/offline machine or equivalent cold-root environment. Never copy `federation-root.identity.json` to the online signer.

```bash
export SYNERGY_FEDERATION_SOURCE=/secure/synergy_system/config/federation_trust_source_v1.json
export SYNERGY_FEDERATION_ROOT_PUBLIC=/secure/export/federation-root.json
export SYNERGY_FEDERATION_ROOT_SECRET=/secure/cold/federation-root.identity.json

scripts/federation_offline_root.sh root-init
```

The root public document may be exported to the online environment; the root private identity remains offline.

## 2. Online HSM signer key generation

On the protected online signing node install the pinned stack and systemd profile:

```bash
sudo bash scripts/install_oqs_ubuntu.sh
sudo bash scripts/install_synergy_federation_stack.sh
sudo bash scripts/install_federation_systemd.sh
sudo editor /etc/synergy-federation-hsm.env
```

Configure the vendor PKCS#11 module, token label, unique key label and a protected PIN file. Then initialize the signer:

```bash
set -a
source /etc/synergy-federation-stack.env
source /etc/synergy-federation-hsm.env
set +a
sudo -E /usr/local/libexec/synergy-federation-hsm-operator hsm-init
sudo -E /usr/local/libexec/synergy-federation-hsm-operator hsm-check
```

The key is generated with `SENSITIVE=true`, `EXTRACTABLE=false` and `PRIVATE=true`. Immediately after generation SHTTPS asks the HSM to sign an interoperability challenge and verifies it through OQS. A format/mechanism mismatch fails closed.

Export only `registry-signer.public.json` to the offline Root environment.

## 3. Offline signer certification + signer revocation state

On the cold Root machine:

```bash
scripts/federation_offline_root.sh issue-signer-cert \
  /secure/import/registry-signer.public.json \
  /secure/export/registry-signer.certificate.json 1

scripts/federation_offline_root.sh revocations-init \
  /secure/export/registry-signer.revocations.json
```

The default signer certificate is short-lived and permits only lifecycle signing. Copy the public Root document, signer certificate and signer revocation state to `/etc/synergy/federation/` on the online signing node.

## 4. Registry Sequence 1 + 51 repositories + Auto-Company control principal

On the online node:

```bash
set -a
source /etc/synergy-federation-stack.env
source /etc/synergy-federation-hsm.env
set +a
sudo -E /usr/local/libexec/synergy-federation-preflight
sudo -E /usr/local/libexec/synergy-federation-hsm-operator provision-initial
sudo -E /usr/local/libexec/synergy-federation-hsm-operator verify
```

`provision-initial` creates independent SHTTPS node identities for the canonical 51 capability repositories plus the separate `synergy_ai_company` control principal and emits delegated Registry Sequence 1 signed by the HSM key.

Node transport identities are still protected file secrets in this version. They are **not** falsely represented as HSM-resident. A separate per-service HSM identity provider is required before those keys can also become non-exportable.

## 5. Automatic online maintenance

Before enabling the timer, test the one-shot:

```bash
sudo systemctl start synergy-federation-maintenance.service
sudo systemctl status synergy-federation-maintenance.service --no-pager
sudo journalctl -u synergy-federation-maintenance.service -n 100 --no-pager
```

Then:

```bash
sudo systemctl start synergy-federation-maintenance.timer
sudo systemctl list-timers synergy-federation-maintenance.timer
```

The systemd service performs:

```text
preflight
  -> HSM interop check
  -> verify root/certificate/revocations/registry/rollback state
  -> rotate node identities if due OR renew registry if due
  -> HSM signs Registry N+1
  -> atomically publish Registry N+1
  -> promote pending node identities
  -> verify again
```

The unit intentionally has no Federation Root private-key condition and `/etc/synergy-federation-hsm.env` is rejected if it contains `SYNERGY_FEDERATION_ROOT_SECRET`.

## 6. Online node revocation

A compromised transport node can be revoked by the delegated signer without waking the Root:

```bash
sudo -E /usr/local/libexec/synergy-federation-hsm-operator revoke-node <NODE_ID>
sudo -E /usr/local/libexec/synergy-federation-hsm-operator verify
```

This changes only node lifecycle state and cannot modify governance/ACL metadata.

## 7. Emergency Registry Signer revocation

A compromised HSM signer is revoked by the offline Root. Bring the cold Root environment online only for the ceremony:

```bash
scripts/federation_offline_root.sh revoke-signer \
  /secure/current/registry-signer.revocations.json \
  <COMPROMISED_SIGNER_ID> \
  /secure/export/registry-signer.revocations.next.json
```

Distribute the new root-signed revocation state to federation services. They reject registries signed by the revoked signer even if the old registry signature itself is cryptographically valid.

Provision a new HSM key under a new label, issue a new Root certificate with a higher generation, and resume registry maintenance with the new signer.

## 8. What the Root still controls

The cold Root is required for:

- initial root generation;
- authorization of a new Registry Signer;
- revocation of a Registry Signer;
- changes to the governance hash (repositories, roles, `rpc_allow`, enabled status, integration metadata);
- Root rotation.

It is **not** required for routine registry renewal, node rotation, node revocation or hash-chain advancement.
