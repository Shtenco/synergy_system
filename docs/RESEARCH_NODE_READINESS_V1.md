# RESEARCH_COMPUTE_NODE readiness v1

This artifact aggregates independent architecture, source, build and service-interface evidence for the first cross-root research node. It is not a process launcher and it cannot grant execution authority.

Current evidence chain:

```text
NodeProfile
→ SourceBuildLock
→ Domain BuildRecipes
→ NodeBuildPlan
+ Domain ServiceSpecs
→ NodeReadiness
```

Current blockers are explicit and independent:

- `BUILD_TOOLCHAIN_NOT_FROZEN`
- `BUILD_ARTIFACTS_NOT_VERIFIED`
- `NEXUS_SERVICE_INTERFACE_NOT_IMPLEMENTED`
- `SYNERGYNET_SERVICE_INTERFACE_NOT_IMPLEMENTED`
- `CONTENT_CACHE_SERVICE_INTERFACE_NOT_IMPLEMENTED`

Therefore the only valid node status in v1 is `NODE_NOT_DEPLOYABLE` and `execution_authority=NONE`.

The readiness verifier re-hashes the domain ServiceSpec bytes and checks source commits/digests against the BuildPlan. A fresh digest cannot remove blockers or retroactively reinterpret library-only service generations as runnable services.

Future build/toolchain and service-interface generations must be additive. A new readiness generation may consume them; this v1 remains immutable provenance.

Canonical readiness digest:

`39a3405b4e5da9b79b260f67f9ec975433ed171d8801eb55edc648b1f38370d8`
