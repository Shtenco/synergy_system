# RESEARCH_COMPUTE_NODE source build-lock v1 — PR summary

This generation freezes the exact source candidates selected for the first cross-root research node composition. It does **not** claim that deployable artifacts were built, tested, reproduced, signed, or approved for execution.

Canonical profile digest:

`406740705e853fa51ad4eacf7a01925fbe4b5cec491be35ea12ba777d217d714`

Canonical source-lock digest:

`14c763218602585d49e12060e1e6cf21d33815fda0cb18711a6522a26157ace2`

Frozen candidates:

- `content-cache` → `Shtenco/synergynet@a8fde01c19420dbe63ca30e1da3b009c0c10064d`
- `nexus` → `Shtenco/agi_nexus@cbc06e83f7f9e242719667e446a090894e11eef1`
- `synergynet` → `Shtenco/synergynet@a8fde01c19420dbe63ca30e1da3b009c0c10064d`

All three services are `SOURCE_CANDIDATE_NOT_BUILD_VERIFIED`; `build_artifact_digest` is intentionally `null` and verifier-enforced. The lock has `execution_authority=NONE`.

A later build-evidence generation must introduce reproducible build inputs/outputs, artifact digests and runner/build attestation. It must not mutate this source-only generation.
