# SUMI compute lease federation bridge — design note

**Date:** 2026-11-25  
**Status:** DESIGN / NOT AN IMPLEMENTED CONTRACT  
**Scope:** bridge the existing Agent Fabric scheduler lease to the existing inference-stage assignment without creating a second scheduler or duplicating domain types.

## 1. Existing authorities and types

The current source has two distinct layers:

1. `node-runtime/crates/agent-fabric` in `synergy_ai_blockchain`
   - `TaskSpec`: task ID, goal, required role/tools, CPU millis, memory MiB, remote policy.
   - `TaskLease`: task ID, agent ID, issue epoch, expiry epoch, commitment version, 32-byte lease root.
   - `SwarmScheduler`: in-memory agent registry and active lease map. PR #32 adds V3 full-task binding and exact active-lease admission within this process.

2. `src/inference.rs` in `synergy_ai_blockchain`
   - `InferenceJob`: job/requester/model/input/plan commitments, output and cost bounds, creation/deadline.
   - `InferenceStageAssignment`: job ID, stage index/kind, worker ID, model-shard/input/resource commitments, lease expiry.
   - `InferenceExecutionPlan`: ordered stage assignments and plan root.
   - `InferenceStageReceipt`: stage/worker/model/input/output/trace/signature commitments and execution measurements.

These types are complementary, not interchangeable. Do not rename or duplicate them in Meta-OS.

## 2. Critical incompatibilities that block a direct adapter

A direct cast from `TaskLease` to `InferenceStageAssignment` is invalid:

- Agent Fabric uses string `task_id` and `agent_id`; inference uses 32-byte `job_id` and `worker_id`.
- Agent Fabric epochs are scheduler counters; inference `lease_expires_at` is a timestamp-like `u64`. Their units and clock authorities are not specified as equivalent.
- `TaskLease.lease_root` binds V3 `TaskSpec` fields, worker string and scheduler epochs. It does not bind inference `model_shard_commitment`, `input_commitment`, `resource_limit_commitment`, `stage_index`, `stage_kind`, or `execution_plan_root`.
- `InferenceStageAssignment` has no Agent Fabric lease root, commitment version, issuer identity, or scheduler signature.
- The active lease map is process-local and volatile. A remote node cannot independently query or prove that a lease is still active using the current `SwarmScheduler` API.

Therefore, the current V3 lease root alone MUST NOT authorize an inference stage.

## 3. Proposed federation envelope

Propose the wire contract name `synergy.compute.lease-binding/v1`. It is an envelope referencing the existing domain objects; it does not replace them.

Required fields:

| Field | Meaning |
|---|---|
| `schema` | Exact value `synergy.compute.lease-binding/v1` |
| `job_id` | 32-byte inference job identifier, canonical hex |
| `stage_index` | Exact index from the canonical execution plan |
| `plan_root` | 32-byte `InferenceExecutionPlan.plan_root`, canonical hex |
| `task_spec` | Canonical serialization of the existing Agent Fabric `TaskSpec` |
| `task_lease` | Canonical serialization of the existing V3 `TaskLease` |
| `stage_assignment` | Canonical serialization/reference of the existing `InferenceStageAssignment` |
| `worker_key_id` | Authenticated transport identity/key identifier bound to the 32-byte worker ID |
| `clock_domain` | Versioned scheduler epoch domain identifier |
| `issued_epoch` / `expires_epoch` | Agent Fabric logical lease window; never silently interpreted as wall-clock timestamps |
| `binding_root` | Domain-separated hash over all preceding execution-authorizing fields |
| `issuer_key_id` / `issuer_signature` | Signature over the canonical envelope digest, issued by the scheduler authority |

The schema must reject unknown fields, duplicate JSON keys, non-canonical encodings, V2 leases, zero commitments, invalid ranges, and mismatched job/stage/worker bindings. The signature algorithm and key policy must use the project's approved standardized cryptographic profile; do not introduce a custom signature scheme.

## 4. Deterministic binding checks

Before a worker can accept a stage:

1. Verify the scheduler signature and key validity/revocation policy.
2. Verify the canonical `InferenceJob` and `InferenceExecutionPlan`; recompute the plan root and select the exact `stage_index`.
3. Require envelope `job_id`, `plan_root`, stage index and serialized assignment to match the selected assignment byte-for-byte after canonical encoding.
4. Require the assignment worker ID to equal the authenticated peer identity's registered 32-byte worker ID.
5. Require the `TaskLease` to be V3, match the exact `TaskSpec`, and bind the same worker. The adapter must use one documented, collision-free mapping between the 32-byte worker ID and Agent Fabric agent ID.
6. Verify `binding_root` over job, plan, stage assignment, TaskSpec, TaskLease, clock domain and issuer identity.
7. Check that the lease is current against a durable/replicated scheduler authority or a verifiable signed lease-state/epoch proof. A process-local map is insufficient for remote admission.
8. Check resource limits against owner-authorized hardware discovery and enforce them in the OS sandbox before fetching or launching any workload.

A destination must fail closed if it cannot establish the clock domain, worker identity, issuer authority, current lease state, or OS-enforced resource policy.

## 5. Clock and identity decisions still required

Do not conflate `expires_epoch` with `lease_expires_at`. Choose one explicit design before implementation:

- **Logical epoch model:** define a monotonic consensus epoch service and encode the stage deadline in that same epoch domain; or
- **Time model:** define a trusted time source, bounded clock skew, timestamp precision, and replay window, then revise the relevant assignment/lease contracts.

Similarly, worker identity needs a single registry mapping:
- Agent Fabric `agent_id` string;
- inference `worker_id: [u8; 32]`;
- PQ-MESH authenticated peer/key identity;
- owner-authorized device identity.

The mapping must be authenticated and rotation/revocation-aware. A display name or self-declared advertisement is not identity proof.

## 6. Receipt and settlement lifecycle

A valid lease binding only authorizes an attempt; it is not proof of execution.

After execution:
1. Worker emits the existing `InferenceStageReceipt` with output, trace, model, input, worker and measurement commitments.
2. Receipt is transported over the authenticated PQ-MESH session and checked against the exact assignment and binding.
3. Independent verifier challenges/recomputes the required evidence; worker self-report alone is insufficient.
4. Receipt ID and job/stage/attempt nonce are consumed with durable replay protection.
5. Only independently accepted evidence can flow into the existing reward-eligibility/settlement path. The worker runtime must never mint tokens or write financial ledgers directly.

## 7. Implementation gates

1. Define canonical encodings and vectors for the existing Rust types.
2. Decide worker-ID mapping and clock domain.
3. Add the binding envelope and signature verification in the authoritative scheduler boundary.
4. Persist/replicate lease issue, renewal, revocation and consumption state.
5. Bind the envelope to authenticated PQ-MESH peer identity.
6. Add destination-side tests for wrong job, stage, worker, plan root, model/input/resource commitment, clock domain, issuer key, expired/revoked lease and replay.
7. Only then connect Meta-OS resource discovery and OS sandbox admission.
8. Prove one CPU-only job across two independent hosts, including result return and independent verification.

## 8. Status policy

This document is a design proposal only. Do not add this item to the registry as `ADAPTER_IMPLEMENTED`, do not count it as an integration edge, and do not claim remote execution. Registry promotion requires schema validation, producer and consumer adapters, contract tests, and independent-host E2E evidence.
