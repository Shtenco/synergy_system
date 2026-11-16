# RESEARCH_COMPUTE_NODE build-lock PR note

This branch is additive over the RESEARCH_COMPUTE_NODE profile generation. It introduces `synergy.node-build-lock/v1` as a source/build provenance contract.

Current v1 lock status is deliberately `SOURCE_CANDIDATE_NOT_BUILD_VERIFIED`. Source commits are frozen, but no reproducible deployable artifact digest is asserted until a real build runner produces and verifies those bytes.

The build lock grants no execution, financial, payment, accounting, or architecture authority.
