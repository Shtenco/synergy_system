# RESEARCH_COMPUTE_NODE Build Lock v1 — status

This generation is a **source-candidate lock**, not a deployable build attestation.

Current status:

- node profile bytes are frozen by `synergy.node-profile/v1`;
- NEXUS and SynergyNet source generations are frozen by immutable commit/tree evidence;
- `build_artifact_digest` is intentionally `null`;
- `status = SOURCE_CANDIDATE_NOT_BUILD_VERIFIED`;
- no executable artifact is authorized by this object;
- no Meta-OS service may become runnable merely because this lock verifies;
- a future build-verification generation must add a reproducibly produced artifact digest and independent build evidence.

This file exists to prevent source provenance from being misreported as build reproducibility or deployment readiness.
