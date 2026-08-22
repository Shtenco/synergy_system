# SCIENCE_RESEARCH_NODE source build-lock v3

V3 is an append-only source-identity update for the existing Science Node composition.

It preserves the same:

- node profile digest: `0c9b82e591c5aa30d1f9b499edee02c0b56643af825bbb7eecb93f8651659107`
- capability registry digest: `3727810480e5660129fc63a2d7999b988ed9ae387365d4501bb50b7ae7257913`
- SynergyNet content-cache source
- SynergyNet relay source
- local Science Agent source

The only source identity change is the NEXUS service:

```text
v2 lock: NumPy/float32 SmallWorld service source ef1a6e...
v3 lock: exact-rational stdlib SmallWorld service source 2ee8f2...
```

The v3 lock digest is:

`de35e3f31d85b9ab559180a12535ecdaa58fd70c6d3575d215994064933e1274`

## No build overclaim

V3 remains a source-only lock:

```text
build_artifact_digest = null
build_evidence_digest = null
build_status = SOURCE_CANDIDATE_NOT_BUILD_VERIFIED
verification_status = SOURCE_IDENTITY_FROZEN_BUILD_NOT_VERIFIED
execution_authority = NONE
```

The lock does not prove that any service artifact was built or tested. It only makes the next recipe registry generation internally consistent with the new stdlib NEXUS service source.

Old build-lock v1/v2 generations remain unchanged and valid provenance for their own source selections.
