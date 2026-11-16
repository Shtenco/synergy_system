# Research Compute Node — Readiness v4

This generation is additive to v1/v2/v3 and does not rewrite historical negative evidence.

Readiness v4 consumes the exact domain-owned NEXUS and SynergyNet BuildRecipe v3, BuildEvidence v1 and ArtifactRuntimeSpec v1 plus the shared `synergy.build-toolchain-lock/v1`.

The verifier derives the blocker set from evidence. The canonical fixture is accepted only when:

- all three roles (`content-cache`, `nexus`, `synergynet`) bind exact expected recipe/evidence/runtime-spec digests;
- two recorded builds per artifact are byte-identical;
- artifact SHA-256 and size agree between recipe and both builds;
- all recorded artifact smoke tests PASS;
- the shared deterministic ZIP_STORED builder and toolchain lock match exactly;
- runtime requirements are empty;
- every layer retains `execution_authority=NONE`;
- NEXUS retains `network_access=NONE`, `process_execution_authority=NONE`, `financial_authority=NONE`;
- readiness retains `auto_start=false`.

Canonical roots:

- ToolchainLock: `af92c9f1909ae3b64aaea78bdce2c6d05deb974ad242482b36e0c8ce820a2848`
- ArtifactSet: `14a67cfbe75361a8ca2f3bd43befd3aef97eddc29d4d725bd83f289ed829bc77`
- BuildPlan v4: `8f37d84645e78818b17c884e7c46d1ba680e79a53a2125faab64de42a290953f`
- Readiness v4: `ee20353d76d377f31f8054dae0c6463db4b3aae1a57b4ccfc2d7631e2251a95b`

The resulting canonical blocker set is empty, but the state is deliberately `NODE_ADMISSION_READY_NOT_RUNNING`. Readiness is evidence for an admission decision; it is not a process start, deployment side effect, financial authorization, or execution capability.
