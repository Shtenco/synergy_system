# Science Node service build recipe registry v1

`synergy.service-build-recipe-registry/v1` is an architecture/orchestration metadata object. It does **not** build services and it does **not** grant deployment or execution authority.

It binds the exact `SCIENCE_RESEARCH_NODE` architecture profile, capability registry and source-only build-lock v2 to the three source-owned deterministic build recipes currently defined for the node:

| Recipe owner | Recipe | Service coverage | Dependency state |
|---|---|---|---|
| `Shtenco/agi_nexus` | `NEXUS_SMALLWORLD_SERVICE_BUILD_RECIPE_V1` | `nexus` | NumPy range only; blocks build verification |
| `Shtenco/nexus_science_agent` | `NEXUS_SCIENCE_LOCAL_SERVICE_BUILD_RECIPE_V1` | `science-agent` | Python stdlib only |
| `Shtenco/synergynet` | `SYNERGYNET_RESEARCH_TRANSPORT_BUILD_RECIPE_V1` | `content-cache`, `synergynet` | Python stdlib only |

The current canonical registry intentionally has:

- `artifact_digests = []`;
- `build_evidence_digests = []`;
- `overall_status = BUILD_RECIPES_FROZEN_ARTIFACTS_NOT_EMITTED`;
- `execution_authority = NONE`.

This is a hard boundary. A fresh registry hash cannot upgrade the current generation to build-verified status. Real artifact/evidence digests require a later evidence-bearing generation after source-owned build workflows actually execute.

## Authority separation

The recipe schemas remain owned by their source repositories. `synergy_system` owns only the aggregate recipe registry because its role is to describe the composition of a SYNERGY node. It is not a source build authority.

`synergy_meta_os` may consume the registry as an admission input, but a valid registry is still not sufficient for admission. Meta-OS must independently verify signed manifest, capability registry, node profile, build lock and actual build evidence.

## Service coverage

The registry verifier requires exact, non-overlapping coverage of:

- `content-cache`;
- `nexus`;
- `science-agent`;
- `synergynet`.

No service may disappear or be covered by two recipes without a new registry generation.

## Next generation

After real runners emit deterministic packages and evidence, a new append-only artifact/evidence registry or build-lock generation may reference those digests. This v1 object remains immutable provenance and must not be edited into a successful build after the fact.
