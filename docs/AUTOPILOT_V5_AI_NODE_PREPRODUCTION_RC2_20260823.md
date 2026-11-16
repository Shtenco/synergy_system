# AUTOPILOT V5 AI Node — Pre-Production RC2

RC2 is an additive correction over RC1. It preserves all prior roots and incorporates the newly observed current unavailability of the old SynergyNet Drive locator.

RC2 root:

`03914c9199b25227026d02a2a2b2d0d8a11e958982c76865701729fff55710ba`

## What changed from RC1

Nothing about the artifact identity changed. Exact SynergyNet remains:

`7f22e68d80a7df879af71ebccdb45f8edb10cae3698bf07faa7076ce76fd0ef7` / 12,837 bytes.

What changed is the **present-time locator claim**. The former Drive file id can no longer be resolved in the current connected Drive context. This is recorded by negative evidence:

`2529d725e426c5028daab7346d1c704d643ffd209d35ceace7f7330203a6353f`.

Therefore RC2 records:

- `artifact_identity_status=UNCHANGED_EXACT_REPRODUCIBLE`
- `artifact_resolution_status=BLOCKED_NEW_SYNERGYNET_DURABLE_LOCATOR_REQUIRED`
- `release_stage=PREPRODUCTION_RC2_LOCATION_REMEDIATION_REQUIRED`
- `current_running=false`.

## Production consequence

Before production, SynergyNet must be materialized at a new durable locator and independently verified against exact SHA-256 and size. Only then can the production bootstrap artifact-verification input be populated.

The rest of the production gate remains unchanged: persistent HostProfile, production SupervisorConfig, fresh health/transport roundtrip, fresh DeploymentEvidence, fresh DeploymentResult and explicit governance promotion are still required.

RC2 does not rewrite historical LocationEvidence v2 or LAB deployment evidence. It only prevents stale locator availability from being treated as a current production fact.
