# SCIENCE_RESEARCH_NODE service build recipe registry v2

This generation is an append-only update of the Science Node build recipe set.

## What changed

Only the NEXUS build recipe was upgraded:

```text
v1: nexus.service-build-recipe/v1
    source: ef1a6e...
    dependency status: RANGE_ONLY_BLOCKS_BUILD_VERIFICATION

v2: nexus.service-build-recipe/v2
    source: 2ee8f2...
    recipe commit: d8ef528...
    recipe digest: 3e255804...
    dependency status: STDLIB_ONLY_NO_THIRD_PARTY_RUNTIME_DEPENDENCIES
```

The local Science Agent and SynergyNet Research Transport recipes remain their existing v1 stdlib-only generations.

The registry binds to Science Node build-lock v3:

`de35e3f31d85b9ab559180a12535ecdaa58fd70c6d3575d215994064933e1274`

Canonical registry digest:

`93b92cb99a38f95b044ec2b3123f37ebf90a603c2768ec47556cf72baa8c7529`

## Important status distinction

All current Science Node recipes are now stdlib-only, so the old third-party dependency-range blocker is removed from the selected recipe set.

This does **not** mean artifacts or tests are verified:

```text
artifact_digests = []
build_evidence_digests = []
overall_status = BUILD_RECIPES_FROZEN_ARTIFACTS_NOT_EMITTED
execution_authority = NONE
```

Actual artifact/test evidence remains source-repository-owned. `synergy_system` only records orchestration metadata and cannot manufacture BUILD_VERIFIED status.

Old service build recipe registry v1 remains immutable provenance for the previous NEXUS selection.
