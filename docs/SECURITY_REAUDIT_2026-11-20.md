# SYNERGY Security Re-audit — 2026-11-20

**Scope:** recheck of committed credential-like artifacts and remediation evidence in Cashero, USDS, TURBO Linux and AI Trade Terminal. Credential values are intentionally not reproduced; no credential was tested or used.

## Executive status

**UNRESOLVED — 4 P0 + 1 P1**

Four repositories have unresolved P0 credential/security blockers: the three previously tracked incidents in Cashero, USDS and TURBO Linux, plus a newly detected non-placeholder broker username/password exposure in AI Trade Terminal. Broker-side validity and external rotation/revocation for the new finding remain unverified.

| Repository | Main-tree finding | Security PR | PR branch finding | Current result |
|---|---|---|---|---|
| synergy_cashero | .env, bot1.env, bot2.env, owner.env remain present | No dedicated security PR in current open-PR map | Open PR #8 is provenance-only; #6 is trading/simulation work | Main remains exposed; no rotation/revocation evidence |
| synergy_usds | base-mainnet-deployer.key remains present | #6, ready-for-review | PR changes only .gitignore and SECURITY_KEY_ROTATION.md; key file remains in the PR branch tree | Remediation is incomplete; adding ignore rules does not remove a tracked key |
| synergy_turbo_linux | Linux Ubuntu.ppk remains present | #13, draft | PR removes the key file from its branch and adds an incident report | Candidate repository cleanup only; PR is unmerged and external rotation/revocation is unverified |\n| synergy_ai_trade_terminal | Non-placeholder broker username/password literals in `cassandra_v6_FIXED.py`; authentication and order-placement paths present | No dedicated remediation PR recorded | Not verified | Newly detected P0 candidate; broker-side validity, use and revocation are unverified |

## Repository evidence

### Cashero

Main tree contains the path names:

- .env
- bot1.env
- bot2.env
- owner.env
- .env.example

The prior audit classified the committed environment-file values as non-placeholder credential/private-key-like material. This report does not reproduce those values. The current open-PR map contains no dedicated security-remediation PR: PR #8 documents legacy provenance and PR #6 concerns trading/simulation code.

**Required:** assume all potentially real credentials are compromised; rotate/revoke keys, RPC/API credentials and bot credentials; verify dependent bots/contracts; remove sensitive material from current tree and address Git history under an approved incident plan.

### USDS

Main tree still contains base-mainnet-deployer.key. Security PR #6 is open and not draft, but its changed-file list contains only:

- .gitignore (added)
- SECURITY_KEY_ROTATION.md (added)

The security branch tree still contains base-mainnet-deployer.key. Therefore PR #6 does not currently remove the tracked key file. Its new document correctly describes required rotation, privilege transfer, asset migration, revocation and history remediation, but the document is a procedure, not proof those actions occurred.

**Required:** rotate/revoke the old deployer identity, verify all privileged roles and allowances, remove the key from current tree and perform approved history remediation. Do not treat PR #6 as a completed fix.

### TURBO Linux

Main tree still contains Linux Ubuntu.ppk. Security PR #13 is draft and its branch removes the file, adds .gitignore rules and adds docs/SECURITY_INCIDENT_SSH_KEY_20260904.md. The incident report says the committed PPK was unencrypted and must be treated as compromised.

The branch-side deletion is useful but does not change main until merged. More importantly, the incident report explicitly says it does not prove rotation, host revocation, absence of unauthorized use or history sanitization.

**Required:** identify every authorized host/account, install a newly generated key, revoke the old public key everywhere, review access logs, merge repository cleanup after review and handle Git history under an approved plan.

### AI Trade Terminal\n\nThe current `main` source contains literal, non-placeholder username and password values in `cassandra_v6_FIXED.py`. The same file implements broker authentication and order-placement methods. The credential values are intentionally omitted from this report.\n\n`MAIN.py` also catches failures to start the real collector/tester and enters an infinite heartbeat loop. This can make a failed functional component appear alive to a process-level supervisor.\n\n**Required:** treat the literals as compromised until the broker confirms otherwise; rotate/revoke externally, inspect broker sessions/API permissions and access logs, inspect all Git refs/history, remove the literals from source, and require explicit `READY`/`DEGRADED`/`FAILED` states instead of a healthy-looking fallback loop.\n\n## Governance inconsistency corrected

The prior security blocker registry marked TURBO's deployment blocked but set federation_promotion_blocked=false, despite the confirmed unencrypted private key and the still-present main-tree file. This is inconsistent with the fail-closed security gate.

The registry has therefore been updated to set federation_promotion_blocked=true for TURBO, and its interface status is now SECURITY_BLOCKED. This does not claim the credential was rotated; it prevents the unresolved security incident from being treated as an integrated/promotable node.

## Acceptance criteria — all must be evidenced

1. Fresh credentials generated outside Git and outside ordinary CI logs.
2. Old credentials revoked; on-chain roles/allowances or SSH authorized keys verified as removed.
3. Dependent services, bots, contracts and hosts confirmed to use only new identities.
4. Secret material absent from current main tree.
5. Git history cleanup considered and completed where approved; clones/caches/backups addressed.
6. Secret scanning and CI/pre-commit denial rules active.
7. Independent evidence attached to the incident record.

Until then, all four P0 credential incidents remain UNRESOLVED and deployment-blocked. A file deletion, .gitignore entry, draft PR or written rotation checklist is not credential rotation.


## Additional P1 — cognitive-memory promotion gate (not a credential incident)

Repository: `Shtenco/synergy_hierarchical_cognitive_memory_architecture`, feature PR #1, current head `2d6d7872653b9d525a74046e992a843b2a905d57`.

This P1 is separate from the four committed-credential P0 incidents and is currently present on the Draft feature branch, not established as a main-tree exposure:

1. `synergy_memory/api.py` exposes local API routes without authentication or authorization. The repository documents this as a local-development adapter; do not expose it on a network or promote it as a federated service.
2. Repository ingestion reads files discovered by recursive path traversal without explicit symlink rejection and resolved-path containment enforcement. A crafted symlink can make an ingestion process read outside the declared repository root.
3. The current source index uses URI as a primary key while ingestion stores repository-relative paths. Two repositories ingested into one shared store can collide on the same relative URI and overwrite current provenance.

**Required before promotion:** loopback-only boundary until authenticated identity/authorization exists; reject symlinks and enforce resolved-path containment; namespace source identity by repository ID + normalized path + immutable revision; add adversarial multi-repository regression tests; obtain executed exact-head CI. No external exposure or exploitation is claimed.
