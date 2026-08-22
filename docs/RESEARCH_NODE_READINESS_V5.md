# Research Compute Node — durable-artifact Readiness v5

This generation is additive. Readiness v4 remains immutable historical evidence.

## Why v5 exists

After Readiness v4, two independent changes occurred:

1. the historical NEXUS artifact `fa7bbd…` remained valid historical BuildEvidence, but a later saved build input reconstructed a different deterministic artifact. The correction was a new NEXUS artifact generation (`e87d0080…`, 56,965 bytes), never a mutation of v1;
2. the first central durable-location drafts, ArtifactSet v2 and BuildPlan v5, contained self-digest fields that did not equal canonical re-hashes of their own published JSON. They are retained as negative/superseded evidence rather than edited.

Negative evidence root:

`564dfab1230dc28270dfc392125234208e4762400a6488c5d53a936f3d9bbdaa`

## Canonical v5 chain

- ArtifactSet v3: `bc7d89378424a18727b90072c86e06238ea14e64bfb9dfc4464f184297eddf84`
- BuildPlan v6: `74c32607bc9fdadf43dddc87c58aa58adeaa2d795553d02cba87cf55ca12ec98`
- Readiness v5: `01c706352c6a63d8545373b29999dba9a9d3407bcf5c5e804e3e82a2571e2112`

The central verifier now independently re-hashes domain-owned build inputs/recipes/evidence/runtime specs and artifact-location evidence. A location is accepted only when its evidence binds the exact artifact SHA-256 and size, the exact build evidence, the expected connected-Drive file ID, a PASS pre-upload SHA/size check, and the fail-closed resolution contract:

`FETCH_BY_PROVIDER_FILE_ID_THEN_VERIFY_SHA256_AND_SIZE_BEFORE_EXECUTION`

The resolver must therefore re-check SHA-256 and size after fetching. Presence in Drive alone grants no execution authority.

## Authority boundary

Canonical Readiness v5 is still only:

`NODE_ADMISSION_READY_NOT_RUNNING`

with:

- `auto_start=false`
- `financial_authority=NONE`
- `payment_authority=NONE`
- `accounting_authority=NONE`
- `execution_authority=NONE`

NEXUS additionally retains no network or process-execution authority. Readiness does not authorize MetaPay, Financial OS, treasury, accounting, settlement, or process start.

The next state transition belongs to `synergy_meta_os`: Admission v2, ArtifactRegistry v3 and DeploymentPlan v3. Even after durable locator blockers are removed, host binding, supervisor materialization and executed host evidence remain independent deployment gates.
