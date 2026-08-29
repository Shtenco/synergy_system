# RESEARCH_COMPUTE_NODE build-lock v1 — recovered status

Recovered after interrupted work on 2026-08-22.

The v1 lock intentionally freezes **source identity only**:

- NEXUS small-world candidate: `cbc06e83f7f9e242719667e446a090894e11eef1`
- SynergyNet persistent transport/cache candidate: `a8fde01c19420dbe63ca30e1da3b009c0c10064d`
- RESEARCH_COMPUTE_NODE profile digest: `406740705e853fa51ad4eacf7a01925fbe4b5cec491be35ea12ba777d217d714`

The lock MUST remain non-deployable:

- `build_artifact_digest = null`
- `build_status = SOURCE_CANDIDATE_NOT_BUILD_VERIFIED`
- `verification_status = SOURCE_IDENTITY_FROZEN_BUILD_NOT_VERIFIED`
- `execution_authority = NONE`

The source commits were re-checked against GitHub commit objects before opening the stacked PR. A later build-attestation generation must carry reproducible build/test evidence and exact deployable artifact digests; v1 must not be mutated into that role.
