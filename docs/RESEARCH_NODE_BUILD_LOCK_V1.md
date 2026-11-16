# Research Node source build lock v1

`synergy.node-build-lock/v1` closes the architecture gap between a node profile and the exact source revisions that are candidates for a future deployable build.

## What it proves

The canonical research lock binds the `RESEARCH_COMPUTE_NODE` profile digest to immutable Git source commits for:

- `content-cache` — SynergyNet persistent cache candidate;
- `nexus` — hardened NEXUS V20 small-world kernel candidate;
- `synergynet` — SynergyNet transport candidate.

The current source identities are:

- `Shtenco/agi_nexus@cbc06e83f7f9e242719667e446a090894e11eef1`;
- `Shtenco/synergynet@a8fde01c19420dbe63ca30e1da3b009c0c10064d`.

## What it intentionally does NOT prove

This generation has:

- `build_artifact_digest = null` for every service;
- `build_status = SOURCE_CANDIDATE_NOT_BUILD_VERIFIED`;
- `verification_status = SOURCE_IDENTITY_FROZEN_BUILD_NOT_VERIFIED`;
- `execution_authority = NONE`.

Therefore the lock cannot be substituted for a Meta-OS service artifact digest. It does not prove that a wheel, container, binary, VM image, or package was reproducibly built or tested.

## Why this layer exists

Without a build lock, two manifests could use the same `RESEARCH_COMPUTE_NODE` profile while silently pointing to different source generations. The source lock makes that drift explicit and content-addressed without overstating build evidence.

The next generation must add a reproducible build receipt produced by an actual build pipeline. Only then may a later lock contain non-null executable artifact digests.
