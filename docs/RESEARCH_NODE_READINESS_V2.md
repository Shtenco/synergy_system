# RESEARCH_COMPUTE_NODE readiness v2

This generation is additive above immutable `synergy.node-readiness/v1`.

V1 remains the exact historical statement for the older source set:

- build toolchain not frozen;
- build artifacts not verified;
- NEXUS service interface not implemented;
- SynergyNet service interface not implemented;
- content-cache service interface not implemented.

V2 does not edit that history. It introduces `synergy.node-source-revision/v1` for the new SynergyNet runtime generation and distinguishes two hash domains:

- runtime source commit `aa93e18bdeb84a8475419cde83f149c8381428cd` — the exact parent containing executable content-cache and relay runtime code;
- build source commit `d2f5256825f4ee3e878476556a427b3172cf5d31` — the exact source generation containing those runtimes plus ServiceSpec v2 and used by BuildRecipe v2.

NEXUS remains unchanged at `cbc06e83f7f9e242719667e446a090894e11eef1` and remains library-only in ServiceSpec v1.

## Evidence chain

```text
RESEARCH_COMPUTE_NODE profile
        ↓
immutable SourceBuildLock v1
        +
NodeSourceRevision v1
        ↓
SynergyNet ServiceSpec v2
NEXUS ServiceSpec v1
        ↓
SynergyNet BuildRecipe v2
NEXUS BuildRecipe v1
        ↓
NodeBuildPlan v2
        ↓
NodeReadiness v2
```

The central verifier re-hashes the mirrored domain-owned ServiceSpec and BuildRecipe bytes and checks the runtime-source/build-source distinction before deriving readiness.

## Resolved blockers

V2 evidence proves that two source-level service interfaces now exist:

- `CONTENT_CACHE_SERVICE_INTERFACE_NOT_IMPLEMENTED` → resolved;
- `SYNERGYNET_SERVICE_INTERFACE_NOT_IMPLEMENTED` → resolved.

This is not a manual status edit. The resolved set is derived from the v1 blocker set minus blockers still implied by current evidence.

## Remaining blockers

Exactly three blockers remain:

- `BUILD_ARTIFACTS_NOT_VERIFIED`
- `BUILD_TOOLCHAIN_NOT_FROZEN`
- `NEXUS_SERVICE_INTERFACE_NOT_IMPLEMENTED`

The Research Node therefore remains:

- `node_status = NODE_NOT_DEPLOYABLE`
- `execution_authority = NONE`

Canonical digests:

- source revision: `3baac7cb6277e1d73110f7acf35de464233c8debfc1e5a3b0f595de303369d21`
- build plan v2: `1993b95cb0b41584429c35f432f8a10d35a21dd72381e2f7821515769556e2b3`
- readiness v2: `b590134ce5c6246bd686ff3bf3678a5ffc75524e7034f5dfdc14587cbfe16994`

## Next boundary

There are now two independent workstreams:

1. NEXUS: assemble a minimal bounded service core from multiple canonical reasoning/runtime kernels before ServiceSpec v2; do not call the migrated SmallWorld kernel alone a complete NEXUS service.
2. Build reproducibility: freeze the actual Python build toolchain/dependency graph and emit independently verified artifact bytes. A source commit or ServiceSpec digest remains insufficient for Meta-OS process admission.
