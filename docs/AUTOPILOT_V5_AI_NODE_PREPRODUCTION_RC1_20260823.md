# SYNERGY AUTOPILOT V5 AI Node — Pre-Production RC1

This release manifest is the federation-level closure object for the AUTOPILOT V5 + exact NEXUS + SMM AI + SynergyNet node after executed LAB verification.

It does **not** promote the node to production and does not mutate any historical or canonical upstream root.

## Release root

`717b473fc67fbbdef89385d04b260ae2c8a8e85c75365ba8627785e1c8c271c7`

The manifest binds:
- AUTOPILOT integration root `a793250a…`
- DeploymentReference v1 `19375c02…`
- System Registry v2 `12bdca33…`
- SynergyNet transport binding `3c8198e1…`
- Meta-OS Admission v2 `4d3502db…`
- executed LAB result `011c3ce2…`
- AI Blockchain deployment commitment v2 `1b47ae40…`
- Production Transition Gate `fd3f97c1…`
- exact NEXUS `e87d0080…`
- exact SynergyNet `7f22e68d…`
- release ZIP SHA `afba4eb7…`, size `1,045,560`.

## Current claim

`PREPRODUCTION_RC1_NOT_PRODUCTION`

The LAB run reached `RUNNING_VERIFIED` and then all processes stopped gracefully. Therefore `current_running=false`.

GitHub Actions are recorded as `NOT_EXECUTED_UNKNOWN_STEPS_NULL` because the relevant jobs produced no executable step/log evidence. This status must not be rewritten to PASS from the workflow conclusion field alone.

## Production gate

Promotion requires all seven fresh production inputs already defined by Meta-OS Production Transition Gate v1: persistent production HostProfile, production SupervisorConfig, fresh artifact verification, fresh health/transport roundtrip, fresh DeploymentEvidence, fresh DeploymentResult and explicit governance promotion.

No financial, payment, accounting, blockchain-submission or execution authority is granted by this release manifest.
