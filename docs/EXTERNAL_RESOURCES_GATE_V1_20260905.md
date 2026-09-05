# SYNERGY External Resources Gate v1

Status: `BLOCKED_AWAITING_EXTERNAL_RESOURCES`

This contract records the minimum real-world inputs that cannot be produced by repository code alone. It exists to prevent future agents, tests or maintainers from confusing a structurally complete fixture with a real economic execution or external deployment.

## Seven required external resources

1. **One real payment/provider account** supporting payment/capture plus refund/reversal and provider-generated references/webhooks/API evidence.
2. **An eligible merchant/operator entity** accepted by that provider for the intended corridor.
3. **A settlement bank account or wallet** accepted by the provider and reconcilable to the canary transaction.
4. **A deliberately small real canary amount.** The amount may be small; the important property is that the transaction is economically real and externally evidenced.
5. **A public HTTPS webhook endpoint** capable of receiving authenticated provider events and retaining immutable evidence references.
6. **Three distinct persistent external hosts** for the Economic Testnet, each with durable state, a unique host fingerprint, restart-recovery evidence and a non-loopback endpoint.
7. **A safe execution-access path**: an operator-controlled connector or operator-run bootstrap procedure. Raw API keys, wallet private keys, seed phrases, signing keys and SSH private keys must never be pasted into chat or committed to Git.

## What these resources unlock

### A. Real Economic E2E

The existing live-cycle contract requires one causal External Value → Next Capacity run. A single bounded payment-provider canary is the preferred first proof because it can provide the three external evidence moments required by the current 12-phase protocol: external value/settlement evidence, MetaPay utilization/settlement evidence, and later provider refund/reversal evidence.

The provider account alone does not close the gate. A later independent verification generation must inspect the actual provider evidence and bind it to the exact Financial OS and MetaPay artifacts from the same `run_id`.

### B. External three-host Economic Testnet

The deployment gate requires exactly three real persistent external hosts. Three containers on one host, localhost processes, or synthetic CI runners do not satisfy this requirement. Each node must produce HostProfile, SupervisorConfig, host-fingerprint, artifact-verification, durable-storage, restart-recovery, deployment-result and transport-endpoint evidence. Cross-host checkpoint propagation must be non-loopback and captured in a transcript digest.

### C. First MetaPay revenue corridor

The first corridor is intentionally a capped canary, not a broad production launch. Minimum target topology:

`external payer/treasury -> approved provider -> MetaPay -> settlement/reconciliation -> Financial OS -> bounded human-approved utilization -> provider refund/reversal -> reversal accounting -> restored next-cycle capacity`

Only externally realized and reconcilable fees/spread/service revenue may be recognized as external revenue. Minting, internal transfers, token-price changes, LP marks, flash-loan principal and internal revaluation are never external profit.

## Authority boundary

Resource availability is capacity, not authorization.

- financial authority: NONE
- payment authority: NONE
- accounting authority: NONE
- execution authority: NONE
- signing authority: NONE
- blockchain submission authority: NONE
- production deployment authority: NONE
- merge authority: HUMAN_MAINTAINER_ONLY
- auto-merge: false

A future operator may provision resources and approve a capped canary. AI/NEXUS may prepare manifests, validate evidence, detect inconsistencies and generate bounded recommendations, but may not independently authorize or sign a real transaction, deployment, accounting close or merge.

## Security rule

`NO_RAW_SECRETS_IN_CHAT_OR_GIT`

References to credentials are allowed; credential bytes are not. The 2026-09-04 TURBO Linux committed-SSH-key incident is a concrete reason this rule is fail-closed.

## Completion rule

This gate may move from `BLOCKED_AWAITING_EXTERNAL_RESOURCES` only through a new additive evidence object that identifies each fulfilled requirement without embedding secret material. Presence of a domain, VPS IP, provider catalog entry or API-key reference by itself is not proof of readiness or authorization.
