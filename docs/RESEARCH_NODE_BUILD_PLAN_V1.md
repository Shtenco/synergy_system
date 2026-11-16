# RESEARCH_COMPUTE_NODE build plan v1

This generation aggregates already-frozen architecture/source identity with **domain-owned build recipes**. It does not build software and it does not grant execution authority.

Causal chain:

```text
RESEARCH_COMPUTE_NODE profile
        ↓
source build-lock
        ↓
NEXUS domain build recipe
+
SynergyNet domain build recipe
        ↓
node build plan v1
```

The architecture root independently verifies the bytes/digests/source commits/status of the supplied recipes, but it does not decide how NEXUS or SynergyNet should be packaged. `synergy.build-recipe/v1` is therefore an explicit multi-producer contract whose producer is always the repository describing its own build metadata.

Current status is deliberately fail-closed:

- NEXUS toolchain/runtime dependency set is not content-addressed;
- SynergyNet build toolchain is not content-addressed;
- no reproducible wheel artifact has been demonstrated;
- all `build_artifact_digest` fields are null;
- `plan_status = BUILD_PLAN_NOT_REPRODUCIBLE_YET`;
- `execution_authority = NONE`.

A later generation may consume frozen toolchain/dependency locks and independently reproduced artifact hashes. It must be additive and must not rewrite this source-candidate plan.

Canonical plan digest:

`809a23879e9e314b835956ef96cec8ede1faaeef1e5c2c06fd7330df600417aa`
