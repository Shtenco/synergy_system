# SYNERGY Repository Engineering / Security Baseline v1

Date: 2026-09-04

Status: **POLICY + ASSESSMENT CONTRACT DEFINED — NO 42/42 COMPLIANCE CLAIM**

## Goal

Turn the 42-repository SYNERGY federation into an auditable engineering portfolio instead of treating every repository as if it had the same release/security requirements.

Policy root:

`8ba39de2763c72eb99e7586c34bbbeac6caac9cf5904639373d6eca5a0d883ec`

Federation v2 root:

`7de7c2dda23db2581294176bb262ae4aa8cbdc4ba97cdd4326278e88a9713a05`

## Five profiles

### RUNTIME_PRODUCT

For operational/core/product repositories. Required controls include dependency locking or explicit no-dependency evidence, tests, CI, secret hygiene, commit-bound build identity, SBOM on release, reproducibility or documented exception, release policy and Artifact/Evidence Envelope adoption.

### ENGINEERING_TOOLING

For engineering agents/code/compression/science tooling. It carries essentially the same supply-chain expectations as runtime products because tooling can influence downstream artifacts.

### RESEARCH

Research is not forced to pretend to be production. It must instead declare research status, preserve source/data provenance, use tests or an explicit research note, avoid secret material, bind dependencies or declare none, and prohibit production claims without promotion evidence.

### PRESENTATION

Public presentation surfaces need source/deployment identity, secret hygiene, explicit no financial/execution authority and a human-controlled deploy/release policy. A website cannot become an execution authority simply because it displays financial or blockchain data.

### LEGACY_PLACEHOLDER

Historical/placeholder repositories preserve provenance, declare their lifecycle status and explicitly carry no production/operational authority.

## Fail-closed evidence model

Every repository/control assessment is one of:

- `NOT_ASSESSED`
- `EVIDENCED_PASS`
- `EVIDENCED_FAIL`

`NOT_ASSESSED` is the default when evidence is absent. It cannot carry an evidence digest.

`EVIDENCED_PASS` and `EVIDENCED_FAIL` both require an explicit SHA-256 evidence identity and evidence source.

The portfolio status is derived, not user-selected:

- any evidenced failure -> `EVIDENCED_FAILURE_PRESENT`
- all controls evidenced pass -> `EVIDENCE_COMPLETE_PENDING_INDEPENDENT_REVIEW`
- otherwise -> `INCOMPLETE_NOT_ASSESSED`

Even the all-pass state does **not** set `portfolio_compliance_claim=true`. Independent review / human promotion remains a separate boundary.

## Authority boundary

The baseline policy grants no financial, payment, accounting, execution, signing, blockchain submission, production deployment, merge execution or AI authority.

Canonical merge policy remains `HUMAN_MAINTAINER_ONLY`; `auto_merge=false`.

## Why this matters

This prevents three recurring portfolio failure modes:

1. a research repository being presented as production merely because code exists;
2. a product repository being called secure/reproducible because a workflow file exists without executed evidence;
3. one central AI/governance artifact silently acquiring authority over finance, payments, signing or deployment.

## Current evidence boundary

This generation defines the policy and the assessment verifier. It does not claim to have collected all per-repository evidence yet. The next phase is a connector/live audit that emits evidence records into this contract; missing evidence must remain `NOT_ASSESSED`.

Workflow definitions are not CI PASS by themselves. PASS may only be reported when an executed job and its step conclusions are observed.
