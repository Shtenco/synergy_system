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

**Compatibility gate:** before merging, search every verifier, receipt producer/consumer, evidence fixture, and persisted record for V2 assumptions. V2 values must remain explicitly versioned legacy values; they must not be silently interpreted as V3. The repository code-search connector returned no matches during this pass, which is not sufficient proof that no references exist.

### AF-03 — stdio adapter narrows untrusted numeric inputs without range checks (MEDIUM)

In `agent-fabric-stdio.rs`, JSON unsigned integers are read as `u64` and cast to `u32` for CPU and memory. Values above `u32::MAX` truncate rather than being rejected. Missing or wrongly typed values also fall back to defaults. This weakens the boundary between an untrusted JSON-RPC request and scheduler policy.

**Remediation proposed in Agent Fabric PR #32:** strict numeric conversion/range checks, bounded identifiers and tool arrays, and JSON-RPC invalid-params errors. The change is not yet merged or test-verified. Do not silently coerce malformed resource declarations.

### AF-04 — JSONL request size is unbounded (MEDIUM)

The stdio loop reads each request as a complete line without a configured maximum length. A local client able to write to the process stdin can force excessive allocation before JSON parsing.

**Remediation proposed in Agent Fabric PR #32:** a bounded 64 KiB frame reader and a regression test for oversized input. The current behavior fails closed by returning an I/O error (terminating the stdio process); production supervision/restart policy remains to be specified. Malformed UTF-8/JSON and exact boundary behavior still require CI/runtime verification.

### AF-05 — Scheduler is not a remote execution protocol (ARCHITECTURAL GATE)

The inspected shared scheduler tracks CPU millis, memory MiB, tools, remote eligibility and leases. It does not itself establish authenticated remote execution, input/model delivery, sandbox launch, output return, independent verification, or durable receipt consumption. The current P7 evidence also explicitly lists remote execution over PQ-MESH and three-independent-device evidence as pending.

**Required gate:** keep the scheduler as control plane. Do not represent a lease as proof that work ran. A separate worker protocol must bind job, lease, worker identity, input/model hashes, runtime policy, output hash and independent verification.

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

**Required remediation:** use a supervisor transaction: stage and validate all launch specifications, start under a tracked activation generation, health-check, commit only after readiness, and on failure terminate/wait/kill all newly started processes while preserving the old generation. Test child crash, timeout, hung shutdown and partial launch.

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
- No Rust tests, Python tests, clippy, Windows build, Linux sandbox test, or cross-host execution were run in this review.
- No merge was performed.
