# AUTOPILOT V5 AI Node Pre-Production RC3

RC3 consumes SynergyNet LocationEvidence v3 and closes the locator-remediation blocker introduced in RC2.

- RC2: `03914c9199b25227026d02a2a2b2d0d8a11e958982c76865701729fff55710ba`
- SynergyNet LocationEvidence v3: `b1ca1c1f5849deac30a0aac14748c21b8a74a26776ba2134a448c9427a839220`
- RC3: `be8ca90e514e72ddccdc67a38cdd9b8321c2b55eb17ba6f04a9c65dbd4a16129`

State:
- exact SynergyNet identity unchanged;
- durable locator restored through immutable Git carrier;
- `artifact_resolution_status=RESOLVED_CURRENT_GITHUB_GIT_CARRIER`;
- `current_running=false`;
- stage remains pre-production, not production.

Remaining production requirements are only: persistent HostProfile, production SupervisorConfig, fresh artifact verification, fresh health/transport roundtrip, production DeploymentEvidence, production DeploymentResult and explicit governance promotion.
