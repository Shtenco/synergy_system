# SYNERGY Repository Federation v3 Candidate — 2026-09-05

Status: `AUDITED_SCOPE_EXPANSION_PENDING_HUMAN_REVIEW`

This is an additive candidate, not a canonical replacement for Federation v2.

## Parent

Federation v2 remains immutable and contains 42 repositories.

Parent root:

`7de7c2dda23db2581294176bb262ae4aa8cbdc4ba97cdd4326278e88a9713a05`

The live authenticated repository inventory later exposed three additional repositories. V3 Candidate therefore models 45 repositories without rewriting the v2 root.

## Post-v2 additions

1. `Shtenco/synergy_metachain` — README-only post-quantum/metachain research target. It receives no trust, signing or blockchain-submission authority from this registry.
2. `Shtenco/motherboard_xpu_xml` — structured XPU/EML hardware-software R&D source with an observed workflow surface; latest observed main workflow run was a failure, so no CI PASS is claimed.
3. `Shtenco/print_money_synergychain` — README-only monetary/tokenomics placeholder. It remains bound by the Economic Constitution: internal mint/revaluation is not external profit.

## Evidence audit

The companion `repository_evidence_audit_v1_20260905.json` contains exactly 45 default-branch observations. Scope is intentionally limited to root engineering surface plus selected latest main-branch workflow runs.

It is **not**:

- an exhaustive code audit;
- an exhaustive secret scan;
- a legal/compliance certification;
- a production-readiness certification;
- a claim that workflow presence equals successful CI.

Latest observed main-run truth table includes both successes and failures. Examples of observed success include `binary_quantum_theory`, `ai_compress`, `synergychain.github.io` and `synergy_pay_system`. Observed latest-main failures include `ai_language`, `midas_ai_trading_system`, `agi_olga`, `qr_compress`, `motherboard_xpu_xml`, `blochain_budget`, `sinergy-super-app`, `synergy_app`, `synergychain` and `turbo_linux`. `3D_bars_market_structure` and `agi_nexus` had workflow files but no main-run history observed at this audit depth.

## Security findings preserved fail-closed

The audit binds three known committed secret-like findings:

- `Shtenco/turbo_linux` — committed unencrypted PuTTY private-key material was previously confirmed. A separate remediation PR exists, but external key rotation/revocation remains required.
- `Shtenco/cashero` — committed `.env`, `bot1.env` and `bot2.env` filenames were observed. Their contents were deliberately not opened during this audit.
- `Shtenco/usds` — committed `base-mainnet-deployer.key` filename was observed. Its contents were deliberately not opened during this audit.

The verifier refuses a freshly rehashed audit that silently erases any of these three findings.

`NO_ROOT_SECRET_FILENAME_OBSERVED_NOT_EXHAUSTIVE` is deliberately weaker than PASS: it only means no obvious root-level secret-like filename was observed at the current audit depth.

## Canonical drift

The audit also records strong feature-lineage/main drift for several high-value repositories, notably `synergy_system`, `synergy_financial_os`, `synergy_ai_blockchain`, `synergynet` and `agi_autopilot`. Advanced feature-branch evidence must not be confused with canonical `main` until a human maintainer explicitly promotes it.

## Candidate identities

45-repository evidence audit root:

`450d50d0c746e8c36cd0e5e5036f9aece1b9b48e1bfcbe79052a827f8283172f`

Federation v3 candidate root:

`ded2c2482b0c74a79886cec5ffaf9d37b0392f5a1bc8faa325a94ca516a36022`

## Authority boundary

- canonical promotion: false
- auto-merge: false
- merge authority: HUMAN_MAINTAINER_ONLY
- AI financial/payment/accounting/blockchain-submission/production-deployment authority: NONE
- internal mint/revaluation counted as external profit: false

A successful candidate CI run validates the registry contract and its adversarial invariants only. It does not merge Federation v3, remediate repository security incidents, prove production readiness or create any operational authority.
