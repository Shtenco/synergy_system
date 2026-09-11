# LEGACY DISTILLATION V2 — Import Queue

Canonical owner: `Shtenco/synergy_system`

Nothing in this queue is auto-promoted to production. Every mechanism must pass the listed gate in this repository authority boundary.

| Priority | ID | Family | Action | Occurrences | Test gate | Representative |
|---|---|---|---|---:|---|---|
| P0_REWRITE | M143 | SECURITY_ACCESS_CONTROL | REWRITE_REQUIRED | 319 | `role_pause_reentrancy` | grantRole |
| P0_REWRITE | M035 | DAO_GOVERNANCE | REWRITE_REQUIRED | 227 | `quorum_timelock_role_separation` | setDAO |
| P0_REWRITE | M144 | SECURITY_ACCESS_CONTROL | REWRITE_REQUIRED | 221 | `role_pause_reentrancy` | pause |
| P0_PROMOTE_WITH_GATE | M142 | SECURITY_ACCESS_CONTROL | PROMOTION_CANDIDATE | 517 | `role_pause_reentrancy` | pause |
| P0_REWRITE | M145 | SECURITY_ACCESS_CONTROL | REWRITE_REQUIRED | 166 | `role_pause_reentrancy` | transferOwnership |
| P1_REWRITE | M129 | OTHER_RUNTIME | REWRITE_REQUIRED | 57 | `explicit_owner_and_invariants` | TWAPOracle |
| P1_REWRITE | M150 | SECURITY_ACCESS_CONTROL | REWRITE_REQUIRED | 54 | `role_pause_reentrancy` | pauseByParent |
| P0_PROMOTE_WITH_GATE | M146 | SECURITY_ACCESS_CONTROL | PROMOTION_CANDIDATE | 100 | `role_pause_reentrancy` | syncFromChain |
| P1_PROMOTE_WITH_GATE | M045 | DATA_CONFIG_ABI | PROMOTION_CANDIDATE | 91 | `schema_secret_staleness` | WETH |
| P2_REVIEW_OR_EVIDENCE | M122 | OTHER_RUNTIME | REVIEW_BEFORE_PROMOTION | 249 | `explicit_owner_and_invariants` | founderPending |
| P2_REVIEW_OR_EVIDENCE | M123 | OTHER_RUNTIME | REVIEW_BEFORE_PROMOTION | 222 | `explicit_owner_and_invariants` | totalLP |
| P1_PROMOTE_WITH_GATE | M036 | DAO_GOVERNANCE | PROMOTION_CANDIDATE | 81 | `quorum_timelock_role_separation` | DAOConsortium |
| P1_PROMOTE_WITH_GATE | M147 | SECURITY_ACCESS_CONTROL | PROMOTION_CANDIDATE | 77 | `role_pause_reentrancy` | withdrawNow |
| P1_PROMOTE_WITH_GATE | M037 | DAO_GOVERNANCE | PROMOTION_CANDIDATE | 75 | `quorum_timelock_role_separation` | DAONode |
| P1_PROMOTE_WITH_GATE | M038 | DAO_GOVERNANCE | PROMOTION_CANDIDATE | 70 | `quorum_timelock_role_separation` | getCurrentPrice |
| P1_PROMOTE_WITH_GATE | M148 | SECURITY_ACCESS_CONTROL | PROMOTION_CANDIDATE | 63 | `role_pause_reentrancy` | flushLpBuf |
| P1_PROMOTE_WITH_GATE | M149 | SECURITY_ACCESS_CONTROL | PROMOTION_CANDIDATE | 63 | `role_pause_reentrancy` | onlyOwner |
| P1_REWRITE | M152 | SECURITY_ACCESS_CONTROL | REWRITE_REQUIRED | 20 | `role_pause_reentrancy` | setBuyFee |
| P2_REVIEW_OR_EVIDENCE | M124 | OTHER_RUNTIME | REVIEW_BEFORE_PROMOTION | 153 | `explicit_owner_and_invariants` | adapt |
| P1_PROMOTE_WITH_GATE | M039 | DAO_GOVERNANCE | PROMOTION_CANDIDATE | 55 | `quorum_timelock_role_separation` | _sotaPrice |
| P2_REVIEW_OR_EVIDENCE | M125 | OTHER_RUNTIME | REVIEW_BEFORE_PROMOTION | 145 | `explicit_owner_and_invariants` | isFlushDue |
| P2_REVIEW_OR_EVIDENCE | M044 | DATA_CONFIG_ABI | FIXTURE_OR_PROVENANCE | 228 | `schema_secret_staleness` | token0 |
| P1_REWRITE | M043 | DAO_GOVERNANCE | REWRITE_REQUIRED | 17 | `quorum_timelock_role_separation` | claim_task |
| P1_PROMOTE_WITH_GATE | M040 | DAO_GOVERNANCE | PROMOTION_CANDIDATE | 43 | `quorum_timelock_role_separation` | _dao_health |
| P1_PROMOTE_WITH_GATE | M046 | DATA_CONFIG_ABI | PROMOTION_CANDIDATE | 43 | `schema_secret_staleness` | _update |
| P1_PROMOTE_WITH_GATE | M151 | SECURITY_ACCESS_CONTROL | PROMOTION_CANDIDATE | 40 | `role_pause_reentrancy` | notifyCBFund |
| P1_PROMOTE_WITH_GATE | M048 | DATA_CONFIG_ABI | PROMOTION_CANDIDATE | 37 | `schema_secret_staleness` | PolygonConfig |
| P1_REWRITE | M155 | SECURITY_ACCESS_CONTROL | REWRITE_REQUIRED | 12 | `role_pause_reentrancy` | setFees |
| P2_REVIEW_OR_EVIDENCE | M126 | OTHER_RUNTIME | REVIEW_BEFORE_PROMOTION | 92 | `explicit_owner_and_invariants` | amplificationFactor |
| P1_PROMOTE_WITH_GATE | M049 | DATA_CONFIG_ABI | PROMOTION_CANDIDATE | 30 | `schema_secret_staleness` | getALTNPrice |
| P1_PROMOTE_WITH_GATE | M041 | DAO_GOVERNANCE | PROMOTION_CANDIDATE | 30 | `quorum_timelock_role_separation` | onlyMinter |
| P1_PROMOTE_WITH_GATE | M042 | DAO_GOVERNANCE | PROMOTION_CANDIDATE | 28 | `quorum_timelock_role_separation` | alive |
| P1_PROMOTE_WITH_GATE | M050 | DATA_CONFIG_ABI | PROMOTION_CANDIDATE | 26 | `schema_secret_staleness` | _tx |
| P2_REVIEW_OR_EVIDENCE | M127 | OTHER_RUNTIME | REVIEW_BEFORE_PROMOTION | 66 | `explicit_owner_and_invariants` | notifyHolders |
| P2_REVIEW_OR_EVIDENCE | M128 | OTHER_RUNTIME | REVIEW_BEFORE_PROMOTION | 60 | `explicit_owner_and_invariants` | lock |
| P1_PROMOTE_WITH_GATE | M153 | SECURITY_ACCESS_CONTROL | PROMOTION_CANDIDATE | 18 | `role_pause_reentrancy` | setMutualBoost |
| P2_REVIEW_OR_EVIDENCE | M130 | OTHER_RUNTIME | REVIEW_BEFORE_PROMOTION | 50 | `explicit_owner_and_invariants` | calc_epoch_amount |
| P2_REVIEW_OR_EVIDENCE | M131 | OTHER_RUNTIME | REVIEW_BEFORE_PROMOTION | 47 | `explicit_owner_and_invariants` | mkax |
| P1_PROMOTE_WITH_GATE | M154 | SECURITY_ACCESS_CONTROL | PROMOTION_CANDIDATE | 14 | `role_pause_reentrancy` | pause |
| P2_REVIEW_OR_EVIDENCE | M047 | DATA_CONFIG_ABI | FIXTURE_OR_PROVENANCE | 37 | `schema_secret_staleness` | constructor |
| P2_REVIEW_OR_EVIDENCE | M132 | OTHER_RUNTIME | REVIEW_BEFORE_PROMOTION | 19 | `explicit_owner_and_invariants` | Anchor |
| P2_REVIEW_OR_EVIDENCE | M133 | OTHER_RUNTIME | REVIEW_BEFORE_PROMOTION | 14 | `explicit_owner_and_invariants` | price |
| P2_REVIEW_OR_EVIDENCE | M051 | DATA_CONFIG_ABI | FIXTURE_OR_PROVENANCE | 9 | `schema_secret_staleness` | liquidate |
