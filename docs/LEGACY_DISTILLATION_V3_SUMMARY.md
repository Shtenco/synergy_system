# SYNERGY LEGACY DISTILLATION V3

V3 converts the 200-mechanism V2 registry into a typed Dependency / Value-Flow Graph and 64 canonical primitives.

## Verified scope

- 646/646 YELLOW lineage preserved from V2
- 12,941 behavior units mapped
- 200 mechanisms classified
- 64 canonical primitives
- 28 semantic families
- 14 canonical owners
- 49 federation consumers
- 60/60 local V3 tests pass

## Mechanism disposition

- MERGE: 76
- PROMOTE: 47
- REWRITE: 38
- KEEP-AS-TEST: 37
- DELETE: 2

## Primitive disposition

- PROMOTE: 32
- REWRITE: 21
- KEEP-AS-TEST: 9
- MERGE: 2

## Static value-from-air candidates

| Motif | Severity | Legacy files | Required gate |
|---|---:|---:|---|
| AIR02_SYNTHETIC_FEE_LOOP | CRITICAL | 100 | funded_fee_distribution |
| AIR07_QE_KEEPER_LOOP | CRITICAL | 47 | balanced_counterentry_and_treasury_debit |
| AIR01_SELF_LP_MARK | CRITICAL | 31 | external_settlement_plus_consolidation_elimination |
| AIR04_REFLEXIVE_PEG | CRITICAL | 31 | independent_oracle_plus_reserve_conservation |
| AIR08_FLASH_PRINCIPAL_PNL | CRITICAL | 3 | flash_principal_liability_reconciliation |
| AIR05_BRIDGE_DOUBLE_COUNT | CRITICAL | 2 | bridge_liability_elimination |
| AIR03_ARB_TREASURY_RECOGNITION | HIGH | 22 | net_external_pnl_after_all_costs |
| AIR06_STAKING_SELF_REWARD | HIGH | 2 | funded_reward_obligation |

High-confidence authority write-overlap rows: **233**. These are review candidates, not automatically confirmed bugs.

## Economic constitution

1. Own-token appreciation is not external profit.
2. Self-LP/internal reserve movement is not consolidated income.
3. Flash principal is a liability, never owned NAV.
4. New capital is not revenue.
5. Synthetic yield needs an external payer and settlement evidence.
6. QE/mint needs a balanced reserve/liability/backing counter-entry.
7. Participant deposits remain liabilities until externally settled.
8. Zero cost denominator cannot imply infinite ROI.
9. Scenario output is not an observed accounting fact.
10. Bridge locked asset and mirrored claim cannot both be counted as owned hard assets.

## Promotion semantics

`PROMOTE` means eligible for the owner-specific promotion gate; it does **not** mean production-ready. Primitive-level aggregation is conservative: any rewrite-required lineage forces the shared primitive to remain `REWRITE` until unsafe variants are separated or eliminated.

Cycle findings are static co-occurrence/value-flow candidates. Runtime/fork/settlement/accounting evidence is still required to prove or falsify executable economic loops.
