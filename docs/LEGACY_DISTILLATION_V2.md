# SYNERGY LEGACY DISTILLATION V2

Code-level migration registry for the complete 646-file YELLOW legacy set.

Validated local distillation snapshot, 2026-09-11:

- 646 YELLOW file instances -> 332 unique SHA-256 objects;
- 69 Python source paths parsed with Python AST;
- 157 Solidity source paths structurally parsed;
- 5,653 code units -> 2,651 normalized structural variants -> 221 semantic mechanism clusters;
- 2,271 graph nodes / 9,399 graph edges;
- 1,009 cross-mechanism CALLS edges;
- 3,381 repeated CO_OCCURS_WITH edges;
- 221/221 mechanisms have a canonical owner, test profile and promotion gate;
- direct production imports: 0;
- gate statuses passed: 0.

Promotion classes: 77 REWRITE_REQUIRED, 129 CANDIDATE_AFTER_TEST, 9 SUPPORT_CANDIDATE, 6 legacy utility/plumbing clusters requiring manual review.

The mechanism count is derived per semantic domain after structural deduplication and deterministic TF-IDF clustering; it is not a filename count and is not a production-readiness claim.

Federation rule: `legacy source -> SHA provenance -> mechanism -> one canonical owner -> required test -> promotion gate`.

No legacy mechanism may override the existing constitution: mint/own-token mark/self-LP/flash principal/new capital/unfunded yield are not external profit. Financial authority remains in `synergy_financial_os`; settlement authority remains in `synergy_pay_system`; simulations remain scenario evidence until independently validated.

This repository owns the architecture registry only. Detailed owner manifests are placed in the corresponding authority repositories.