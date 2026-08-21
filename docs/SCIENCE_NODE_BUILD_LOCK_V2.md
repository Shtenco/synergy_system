# SCIENCE_RESEARCH_NODE build-lock v2

`synergy.node-build-lock/v2` is the generic successor to the profile-specific Research Compute source lock v1. V1 remains unchanged.

V2 binds an exact node-profile digest and capability-registry digest to a sorted set of service source identities. Each service separately records source commit/ref/role, optional build artifact digest, optional build-evidence digest and build status.

The canonical Science Node source lock freezes the current service-protocol heads for SynergyNet, NEXUS and Science Agent. All build artifact/evidence digests are intentionally null and overall status is `SOURCE_IDENTITY_FROZEN_BUILD_NOT_VERIFIED`.

A fresh lock hash cannot upgrade that canonical Science Node generation to BUILD_VERIFIED: a new evidence-bearing generation is required after reproducible build/test artifacts actually exist.

Build-lock bytes grant no process execution or domain authority.
