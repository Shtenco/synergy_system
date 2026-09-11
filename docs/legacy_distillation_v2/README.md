# SYNERGY LEGACY DISTILLATION V2

V2 is the semantic migration layer for the legacy YELLOW corpus. It does not copy old repositories wholesale and it does not treat any legacy implementation as production-ready.

Pipeline:

`1206 legacy records -> 646 YELLOW files -> 15,674 atomic units -> 3,847 unique structural shapes -> 200 canonical mechanisms -> 14 canonical authority owners -> executable promotion gates`

Validation on 2026-09-11:

- 646/646 YELLOW files mapped; 0 orphan files.
- 200 mechanism IDs, 28 semantic families.
- 43/43 local falsification/registry tests passed.
- 646/646 source SHA256 values match V1 provenance.
- 0 raw private-key/mnemonic assignment hits in the V2 package.
- deterministic rebuild: mechanism catalog SHA256 reproduced byte-for-byte.

Authority rule: every mechanism has exactly one canonical owner. Other repositories may consume the resulting interface/evidence but must not redefine the authoritative fact.

Promotion classes are: `PROMOTION_CANDIDATE`, `REWRITE_REQUIRED`, `R_AND_D_WITH_GATE`, `FALSIFICATION_FIXTURE_OR_REWRITE`, `FIXTURE_OR_PROVENANCE`, `EVIDENCE_OR_TEST_FIXTURE`, `EVIDENCE_ONLY`, and `REVIEW_BEFORE_PROMOTION`.

`PROMOTION_CANDIDATE` is deliberately not a production-readiness claim. Promotion requires the owner-specific invariant test, code review, and where relevant fork/compiler/security validation.

Core economic firewall:

- own-token appreciation is not external profit;
- internal LP movement is not consolidated income;
- flash principal is not owned NAV;
- new investor capital is not revenue;
- mint/QE/reward/dividend requires an explicit funding/counter-entry path;
- participant deposits remain liabilities;
- bridge destination value requires finalized source lock/burn and replay protection;
- simulation remains `SCENARIO/STRESS/COUNTERFACTUAL`, never self-promoted to `OBSERVED`;
- network/orchestration/UI layers cannot grant themselves financial or signing authority.

The detailed 200-mechanism catalog and per-owner queues are maintained by the distillation artifact and mirrored into authority repositories under `docs/legacy_distillation_v2/`.
