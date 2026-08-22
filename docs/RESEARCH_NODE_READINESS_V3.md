# RESEARCH_COMPUTE_NODE readiness v3

This generation is additive above immutable Readiness v2.

Readiness v2 correctly reported three blockers for its evidence set:

- `BUILD_ARTIFACTS_NOT_VERIFIED`
- `BUILD_TOOLCHAIN_NOT_FROZEN`
- `NEXUS_SERVICE_INTERFACE_NOT_IMPLEMENTED`

The new NEXUS proof-first runtime and ServiceSpec v2 provide independent source evidence for the final missing service interface. V3 therefore introduces a new source revision and build plan rather than editing the v2 blocker list.

## NEXUS update

Runtime source commit:

`4915872c60117bbac0001a0f792f2a8f3a12899a`

Build-source commit containing ServiceSpec v2:

`0cf581fe6ac6e79bcf39c9ed4833e2d5719ddd6f`

ServiceSpec digest:

`c01a22e4dbd5a1e4e6f2b9a3fbc9e49f559a43f1575cd4e6a6f4c22420f3121b`

BuildRecipe digest:

`46e874b075c52ee81e4996c6ce3fc027078f54ad4c4824a869d92b597821fe90`

The service exposes a bounded stdlib proof-first NEXUS core and explicitly does not claim the Ω-R5 neural checkpoint as migrated.

## V3 result

All three required service interfaces are now source-implemented:

- `content-cache` — implemented;
- `synergynet` relay — implemented;
- `nexus` — implemented.

Therefore:

`service_status = ALL_REQUIRED_SERVICE_INTERFACES_IMPLEMENTED_SOURCE_ONLY`

and exactly one blocker is resolved since v2:

`NEXUS_SERVICE_INTERFACE_NOT_IMPLEMENTED`

The remaining blocker set is now exactly:

- `BUILD_ARTIFACTS_NOT_VERIFIED`
- `BUILD_TOOLCHAIN_NOT_FROZEN`

The node remains `NODE_NOT_DEPLOYABLE` and `execution_authority=NONE`. Source-level service completion is not artifact identity and is not Meta-OS process admission.

Canonical digests:

- source revision v2: `82d4b40e2276b8095f7fd3ff2105181d9c038b3e2879265facd022ff30d9fb32`
- build plan v3: `5ac2d5a20428d5e3f88bf25b52137177122cb7d0d3feebf62efeb0576aedddd2`
- readiness v3: `2d2622e82f0a818facdc46a2fac0773107d42b8d8e7b519b4d2fe4030efd1a89`

The next system-wide blocker is no longer NEXUS software service composition. It is reproducible build/toolchain and independently verified artifact evidence.
