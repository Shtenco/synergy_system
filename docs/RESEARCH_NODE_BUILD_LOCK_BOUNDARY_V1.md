# Research Node Build Lock v1 — boundary

`synergy.node-build-lock/v1` is provenance and build-readiness metadata only.

It does **not**:

- start services;
- grant Meta-OS execution authority;
- grant financial/payment/accounting authority;
- prove that a source candidate was reproducibly built when `build_artifact_digest` is null;
- replace the signed node manifest;
- replace the architecture node profile.

The intended chain is:

`NodeProfile -> NodeBuildLock -> SignedNodeManifest -> Meta-OS lifecycle`.

Each arrow is independently verified. A valid object at one layer does not imply validity or authority at the next.
