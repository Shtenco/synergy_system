# Federation production-candidate deployment

This runbook deploys the SYNERGY Federation Trust Registry on a protected Ubuntu/Debian-family signing node. It does **not** claim a completed third-party cryptographic audit. The current OQS provider exports private-key bytes, so this profile is file-secret backed; true non-exportable HSM signing requires a separate HSM provider.

## Pinned cryptographic substrate

- liboqs release 0.16.0, commit `5a1a854b0dc9f2141bdc771c555ee60c37950183`
- liboqs-python release 0.16.0, commit `c6378cd5c8db74c0adf34ddcfbb96ee9c99f8061`
- SHTTPS commit `e8bb87fae6d98417782d51a583d4b9bee7896680`
- ai_compress commit `551fae36eacb5713aa503fc9da2fbc44fe8f2e84`

The preflight requires `ML-KEM-1024`, `ML-DSA-87`, `SLH-DSA-SHAKE-256s`, X25519 hybrid mode and SGH1. A version/algorithm mismatch fails closed.

## Host preparation

Use an encrypted/root-protected filesystem for `/var/lib/synergy/federation/private`. Restrict interactive access to the signing host. Keep independent offline backups of the public root and encrypted private material. Do not copy private node identities into Git or general-purpose configuration management.

From a reviewed checkout of `synergy_system`:

```bash
sudo bash scripts/install_oqs_ubuntu.sh
sudo bash scripts/install_synergy_federation_stack.sh
sudo bash scripts/install_federation_systemd.sh
sudo cp -n config/federation_operator.env.example /etc/synergy-federation-operator.env
sudo chmod 0600 /etc/synergy-federation-operator.env
```

Review `/etc/synergy-federation-stack.env` and `/etc/synergy-federation-operator.env`, then run:

```bash
sudo bash scripts/federation_preflight.sh
sudo bash scripts/federation_first_boot.sh
```

The ceremony refuses to overwrite an existing root/registry. On success it creates one independent identity for each of the 51 capability repositories plus the `synergy_ai_company` control principal and emits Registry Sequence 1.

## First maintenance validation

Before starting the timer:

```bash
sudo systemctl start synergy-federation-maintenance.service
sudo systemctl status synergy-federation-maintenance.service --no-pager
sudo journalctl -u synergy-federation-maintenance.service -n 100 --no-pager
```

Only after the one-shot service succeeds:

```bash
sudo systemctl start synergy-federation-maintenance.timer
sudo systemctl list-timers synergy-federation-maintenance.timer
```

The daily maintenance path runs `preflight -> verify -> rotate/renew -> verify` with no network address family except local UNIX sockets. The service is read-only except for the federation registry/state/private directories.

## Registry renewal and node rotation

Registry lifetime and node-key lifetime are independent. The default policy uses a 30-day signed registry and 90-day node identities. Maintenance renews the registry seven days before registry expiry even if no node key is due. Node identities rotate seven days before their own expiry.

Rotation is crash-safe:

1. create immutable generation secret and `.next` candidate;
2. sign Registry N+1 containing the new public identity and mark the old identity `retiring`;
3. atomically publish Registry N+1;
4. atomically promote `.next` to the stable private identity path;
5. restart the affected service under supervision;
6. after the signed grace window, the old identity is no longer accepted.

A crash before step 3 leaves the old identity active under the old registry. A crash after step 3 but before step 4 remains valid because the old identity is still signed as `retiring` during the grace period.

## Revocation

For a compromised node identity:

```bash
sudo /usr/local/libexec/synergy-federation-operator revoke <NODE_ID>
sudo /usr/local/libexec/synergy-federation-operator verify
```

Then restart federation clients/servers so every process reloads the new registry. Revocation removes the node from derived trust immediately at the next registry load.

## Root key handling

The current implementation signs registry updates with the federation root identity. Therefore the automated file-secret profile requires the root secret on the protected signing node. This is intentionally **not described as offline-root or HSM-backed**. A future delegated-registry-signer/HSM provider should remove the root private key from routine maintenance entirely.

Until that provider exists, compensate by using an encrypted dedicated signing host, strict filesystem permissions, minimal login access, offline encrypted backup, service sandboxing, and independent monitoring of registry sequence/hash changes.
