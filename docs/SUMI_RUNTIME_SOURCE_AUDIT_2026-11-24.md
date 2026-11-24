# SUMI Runtime Source Audit — 2026-11-24

**Status:** SOURCE REVIEW — findings require owner review and remediation  
**Scope:** targeted source inspection of `synergy_ai_blockchain/node-runtime` and `synergy_meta_os/runtime/orchestrator.py`  
**Not performed:** local builds, test execution, Windows runtime validation, Linux sandbox validation, cryptographic audit.

## 1. Executive result

The current code is a useful control-plane and compatibility-runtime foundation, but it is not yet a safe cross-platform remote compute worker. The highest-risk issues are authority enforcement, process isolation, launch integrity, and the boundary between scheduling metadata and actual execution.

The review identified actionable source-level findings below. These are not claims that an attacker has exploited a deployed system; the reviewed Meta-OS file explicitly describes itself as a conventional-Linux development compatibility runtime.

## 2. Agent Fabric — `synergy_ai_blockchain/node-runtime`

### AF-01 — Duplicate agent registration mutates an existing identity (HIGH)

In the previous `SwarmScheduler::register` implementation, `BTreeMap::insert` replaced the existing value before returning whether the key was new. A caller could submit a second `AgentSpec` with the same ID and silently replace role, resource, tool, or local/remote attributes while the method returned `false`.

**Remediation prepared:** PR #32 changes registration to check for an existing ID before insertion and adds a regression test proving that a duplicate cannot replace the original record.

### AF-02 — Lease commitment did not bind the complete task policy (HIGH)

The V2 lease root committed to task ID, goal, agent ID, and epochs, but omitted `required_role`, `required_tools`, `cpu_millis`, `memory_mib`, and `allow_remote`. Two materially different execution policies could therefore produce the same commitment if the included fields matched.

**Remediation prepared:** PR #32 introduces the `SYNERGY/AGENT-LEASE/V3` domain and deterministically commits to all current execution-relevant `TaskSpec` fields plus worker identity and lease epochs. Required tools are a `BTreeSet`, so iteration order is deterministic. Regression tests cover policy-field changes.

**Compatibility remediation added to PR #32:** the public legacy root helpers retain their original V2 hash domain; newly issued leases explicitly carry `commitment_version=V3`; a missing version field on a deserialized legacy `TaskLease` defaults to V2; V2 roots can be checked for migration/audit, but execution admission rejects V2. New scheduler leases are always V3. Regression tests cover both legacy JSON defaulting and V3 serialization.

**Execution-admission hardening added to PR #32:** `validate_for_execution` now requires the expected worker identity and current epoch, rejects not-yet-valid and expired leases, and checks the V3 commitment. `SwarmScheduler::validate_active_lease` additionally requires the worker to remain registered and the exact lease object to equal the scheduler's current active lease; released/replaced leases therefore fail admission. `lease_until` now reclaims expired leases before placement so a missed periodic expiry sweep cannot leave workers blocked indefinitely. Tests cover wrong worker, early/expired epochs, changed lease fields, release/replay rejection and expired-lease reclamation.

**Remaining compatibility gate:** source inspection found the `TaskLease` producer in Agent Fabric and its stdio JSON serialization boundary; `AgentDelegation` carries an opaque lease root and the destination must consult the authoritative scheduler before execution. GitHub code search returned no indexed results, so this is not a complete repository-wide search of evidence archives, external consumers, or persisted deployments. Before merge, validate real historical serialized V2 records and all external consumers. The scheduler check is authoritative only within the lifetime and trust boundary of that scheduler instance; a distributed deployment still needs authenticated, durable lease-state replication or a signed scheduler authority protocol.

### AF-03 — stdio adapter narrows untrusted numeric inputs without range checks (MEDIUM)

In `agent-fabric-stdio.rs`, JSON unsigned integers are read as `u64` and cast to `u32` for CPU and memory. Values above `u32::MAX` truncate rather than being rejected. Missing or wrongly typed values also fall back to defaults. This weakens the boundary between an untrusted JSON-RPC request and scheduler policy.

**Remediation proposed in Agent Fabric PR #32:** strict numeric conversion/range checks, bounded identifiers and tool arrays, and JSON-RPC invalid-params errors. The stdio `task/lease` method now requires an explicit nonzero epoch rather than silently defaulting to epoch 1; a new `task/validate` method performs admission-only validation against the active in-process scheduler lease, expected worker ID and current epoch. The JSON-RPC envelope now rejects null IDs and unknown top-level fields, and each supported method has an explicit parameter allowlist; regression tests cover null IDs, extra envelope keys and unknown method parameters. This endpoint does not launch a process and does not provide durable/federated lease authority. These changes are unmerged and require executable CI validation. The portable CI workflow now includes a separate locked `node-runtime` workspace job (format, metadata, check, tests and Clippy); prior workflow runs failed before runner allocation, so the new gates still need a functioning runner. Do not silently coerce malformed resource declarations.

### AF-04 — JSONL request size is unbounded (MEDIUM)

The stdio loop reads each request as a complete line without a configured maximum length. A local client able to write to the process stdin can force excessive allocation before JSON parsing.

**Remediation proposed in Agent Fabric PR #32:** a bounded 64 KiB frame reader and a regression test for oversized input. The current behavior fails closed by returning an I/O error (terminating the stdio process); production supervision/restart policy remains to be specified. Malformed UTF-8/JSON and exact boundary behavior still require CI/runtime verification.

### AF-05 — Scheduler is not a remote execution protocol (ARCHITECTURAL GATE)

The inspected shared scheduler tracks CPU millis, memory MiB, tools, remote eligibility and leases. It does not itself establish authenticated remote execution, input/model delivery, sandbox launch, output return, independent verification, or durable receipt consumption. The current P7 evidence also explicitly lists remote execution over PQ-MESH and three-independent-device evidence as pending.

**Required gate:** keep the scheduler as control plane. Do not represent a lease as proof that work ran. The local scheduler now has a V3 active-lease admission check, but it is not a distributed authority protocol and does not persist/replicate state. A separate worker protocol must bind job, lease, worker identity, input/model hashes, runtime policy, output hash and independent verification.

## 3. Meta-OS — `runtime/orchestrator.py`

### MOS-01 — Runtime is not importable as a Windows-native backend (HIGH for cross-platform goal)

The module imports Python's `resource` at module import time and uses `preexec_fn` with POSIX resource limits. These are not a Windows Job Objects implementation; on Windows the import and launch path are not portable.

**Required remediation:** move OS-specific imports and launch behavior behind explicit platform adapters. Linux and Windows must implement the same bounded capability/resource contract with independent tests. Windows must use Job Objects and an appropriately restricted process identity; filesystem/network controls need separate enforcement.

### MOS-02 — Artifact hash verification is not bound to the executed command (HIGH)

`verify_service` verifies the declared `artifact` path and SHA-256, but activation launches the supplied `argv` list. Only arguments exactly equal to `$ARTIFACT` are substituted. The manifest can therefore name and hash one artifact while supplying a different executable/command in `argv[0]`.

**Remediation proposed in Meta-OS PR #31:** require `argv[0]` to be exactly the verified `$ARTIFACT`, validate argv shape/length/NULs and SHA-256 syntax, and add an executable-mismatch regression test. This narrows the manifest mismatch but does not eliminate filesystem TOCTOU between hashing and process launch; immutable artifact staging or descriptor-based execution remains necessary for a stronger guarantee. The PR is unmerged and untested.

### MOS-03 — Capability declarations are not enforced by the OS boundary (CRITICAL for untrusted workers)

The orchestrator places capability names in `SYNERGY_CAPABILITIES` for the child process. Environment variables are descriptive metadata, not an access-control mechanism. The inspected launch path does not create a per-service filesystem namespace, network policy, restricted token, seccomp profile, or equivalent OS-enforced capability boundary.

**Required remediation:** do not launch untrusted or volunteer compute workloads through this compatibility path. Implement enforceable per-task filesystem, network, process, device and secret isolation. A worker must never inherit host credentials, private keys, wallet files, or financial-service authority.

### MOS-04 — Attestation is represented as a manifest boolean (HIGH)

High-value roles require `attested` to be truthy, but the inspected code does not cryptographically verify a signature or bind the attestation to node identity, manifest bytes, generation and freshness. An untrusted manifest can set a boolean.

**Required remediation:** define a signed attestation envelope with a trusted key registry, algorithm/key identifiers, canonical manifest digest, node identity, generation/nonce and expiry. Reject missing, stale, revoked or mismatched attestations. Do not treat a boolean as proof.

### MOS-05 — Child stdout/stderr pipes are not drained (MEDIUM/HIGH availability)

Processes are started with `stdout=PIPE` and `stderr=PIPE`, but the orchestrator does not consume these streams. A child that writes enough output can fill a pipe and block indefinitely.

**Remediation proposed in Meta-OS PR #31:** switch child stdout/stderr to `DEVNULL` in the development compatibility runtime, avoiding unread-pipe deadlock, and add a >1 MiB output regression test. This intentionally discards logs; a production runtime still needs a bounded drain/log sink. The PR is unmerged and untested.

### MOS-06 — Failure cleanup is not synchronous or fully transactional (MEDIUM)

On partial activation failure, already launched processes receive `terminate()`, but the code does not wait for termination, escalate to kill after a deadline, or verify that every process exited. The previous active manifest is copied for rollback, but activation failure does not restore a complete previous process set.

**Partial remediation added in Meta-OS PR #31:** activation failure now signals each started service's dedicated POSIX process group, waits for the direct child, escalates to SIGKILL after a bounded grace period, and reaps the child. This also targets descendants that outlive the service leader. A failure-injection regression test covers partial launch failure; an additional Linux process-tree test starts a descendant and checks that group cleanup removes it. This narrows process leaks during partial launch failure, but is not a complete supervisor transaction. **Still required:** stage and validate all launch specifications, track activation generations, health-check before commit, preserve the old generation, and test child crash, timeout, hung shutdown and rollback.

### MOS-07 — Resource limits are incomplete for compute workers (HIGH)

The current limits cover address-space memory, CPU seconds and open files. They do not bound process count, disk use, I/O, network bandwidth, GPU/VRAM, accelerator access or wall-clock deadline. The current limits also do not provide a portable CPU quota model.

**Required remediation:** define a versioned resource profile with hard/soft limits and explicit unsupported-feature behavior. Reject a job if its required isolation or resource control is unavailable; never silently downgrade to weaker controls.

## 4. Required implementation sequence

1. Land and validate the narrow Agent Fabric identity/commitment fix only after V2/V3 call-site compatibility review.
2. Harden stdio request parsing and numeric validation.
3. Specify a canonical signed compute-job and resource-profile contract in `synergy_system`.
4. Refactor Meta-OS into portable policy plus Linux and Windows process adapters.
5. Close executable-to-digest binding, cryptographic attestation, OS-enforced capabilities and bounded output handling before running untrusted workers.
6. Implement CPU-only remote execution across two independent hosts, then three independent devices, with failure injection and independent verification.
7. Add GPU discovery/execution only after CPU worker isolation and end-to-end evidence pass.

## 5. Evidence status

- Agent Fabric source was fetched from GitHub `main`; PR #32 contains proposed registration, lease-commitment and stdio-boundary hardening on a separate branch.
- Meta-OS source and its current test file were inspected from GitHub `main`; PR #31 contains proposed executable binding, strict manifest/limit validation and output-pipe hardening on a separate branch.
- The P7 status file records prior test results but also records remote execution, production sandboxing and independent-device deployment as pending.
- Agent Fabric PR #32 now includes explicit V2/V3 serialization compatibility; V3-only admission bound to expected worker identity and current epoch; exact active-lease comparison against the in-process scheduler; rejection after release/replacement; and reclamation of expired leases before new placement. Regression tests cover these cases. This is an in-process scheduler authority check, not durable/federated lease consensus. The stdio adapter additionally exposes `task/validate` and rejects lease requests that omit the current epoch; both behaviors have regression tests.
- Agent Fabric PR #32 additionally rejects null JSON-RPC request IDs, unknown envelope fields and method parameters outside explicit allowlists; protocol/trust-boundary documentation is in `node-runtime/docs/AGENT_FABRIC_STDIO_PROTOCOL.md`.
- Agent Fabric PR #32 adds a dedicated locked CI job for the `node-runtime` workspace (metadata, rustfmt, check, tests, Clippy) on Rust 1.85.0. This closes a CI coverage gap: the previous portable job ran Cargo commands from the repository root and did not build the separate `node-runtime` workspace.
- Latest observed Actions runs for head `f19dac2d98d2681c4f3b6e3850aea3d5af2287d7` (#1895 / 45434815731 and #47 / 45434815517) failed before runner allocation. Both `rust-portable` and the new `agent-fabric-runtime` job report `runner_id=0` and `steps=[]`; no Cargo command ran. Earlier pre-step failures were reproduced on multiple commits.
- Meta-OS PR #31 now includes POSIX process-group termination for activation cleanup, escalation to SIGKILL, direct-child reaping, a partial-activation failure-injection test and a Linux process-descendant cleanup test. The latest branch head is `98c166f4bd8f6e54ef8b3ce1d969ae64437f9b6a`; no associated workflow runs were returned and the Python tests have not been executed in this environment.
- The new stdio regression tests explicitly cover legacy JSON without `commitment_version` defaulting to V2 and scheduler-issued JSON declaring V3. The new Meta-OS failure-injection test is committed but not executed. No Rust tests, Python tests, clippy, Windows build, Linux sandbox test, or cross-host execution were run in this review.
- No merge was performed.


## 6. Follow-up evidence update — 2026-11-25

- Agent Fabric PR #32 latest head: `6287cdce08ba23e1cda5e3bc678e3cc26984de17`; latest Portable Rust workflow run #45478667661 failed with empty step arrays for both jobs, so no source-level CI result is available.
- Meta-OS PR #31 latest head: `5d1949407c00396866c7e4c63eaafabf744ff936`; process-tree cleanup, duplicate JSON object-key rejection at all nesting levels, duplicate service-name rejection, and corresponding regression tests are proposed but unexecuted.
- Both PRs remain Draft and unmerged. Their code is not production-ready and has not passed executable validation in this work session.

- Meta-OS manifest parsing now rejects duplicate object keys (including nested objects) rather than accepting last-key-wins ambiguity, and rejects duplicate service names before activation.

- The Linux process-tree regression test was made resilient to the `/proc/<pid>/stat` entry disappearing between the existence check and read; latest Meta-OS head is `5d1949407c00396866c7e4c63eaafabf744ff936`.


## 7. Compute lease federation bridge

A separate design note, `docs/SUMI_COMPUTE_LEASE_FEDERATION_BRIDGE_2026-11-25.md`, maps the existing Agent Fabric `TaskSpec`/`TaskLease` to the existing `InferenceJob`/`InferenceStageAssignment`/`InferenceStageReceipt` without duplicating domain types. It documents the incompatibility between logical scheduler epochs and inference expiry timestamps, the missing binding of model/input/resource/stage commitments into the current V3 task lease, the need for authenticated worker identity and durable lease authority, and the required receipt/replay/verification lifecycle. This is DESIGN ONLY; it is intentionally not registered as an implemented contract or runtime edge.
