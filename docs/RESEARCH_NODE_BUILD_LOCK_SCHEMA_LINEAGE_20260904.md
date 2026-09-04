# Research Node Build Lock schema lineage note

Date: 2026-09-04

## Finding

The historical file `schemas/synergy_node_build_lock_v1.schema.json` describes a top-level shape based on `node_profile_digest/status/components/build_artifact_digest/digest`.

That shape does **not** match the canonical source-only v1 implementation, fixture or documentation already used by the research-node lineage:

- runtime: `src/synergy_system/node_build_lock_v1.py`
- fixture: `fixtures/node_build_locks/research_compute_node_source_candidate_v1.json`
- documentation: `docs/RESEARCH_NODE_BUILD_LOCK_V1.md`

The implemented source-only contract uses:

`schema / lock_id / profile_digest / services / verification_status / execution_authority / lock_digest`.

Each service is explicitly `SOURCE_CANDIDATE_NOT_BUILD_VERIFIED` with `build_artifact_digest=null`.

## Resolution

The historical incompatible schema file is preserved unchanged as provenance. It is not silently rewritten.

A new canonical schema profile was added:

`schemas/research_source_node_build_lock_v1.schema.json`

with schema-profile id:

`synergy.research-source-node-build-lock/v1`

The payload itself continues to identify as `synergy.node-build-lock/v1`, matching the existing runtime/fixture lineage.

The schema regression test now validates the canonical fixture against the new source-lock profile and separately asserts that the old incompatible draft does **not** match the canonical fixture.

## Authority / evidence boundary

This correction does not promote the source lock to a verified build. It continues to prove only frozen source identity. Build artifact digests remain null; execution authority remains NONE.
