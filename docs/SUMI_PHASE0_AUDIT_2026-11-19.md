# SUMI Phase 0 — Repository and integration audit

**Document:** SUMI-PHASE0-AUDIT-2026-11-19  
**Program:** SYNERGY Universal Mesh Internet & Compute Fabric (SUMI)  
**Scope:** evidence-based initial audit of the canonical architecture registry and selected repositories  
**Audit date:** 2026-11-19  
**Status:** PARTIAL AUDIT — source/build verification remains open

## 1. Executive result

SUMI should not be implemented as a greenfield rewrite. The inspected repositories already contain meaningful components for PQ mesh transport, agent scheduling, capability-bound service orchestration, hardware metadata, compression evidence and blockchain trust.

The central gap is not the absence of all building blocks. It is the missing end-to-end, cross-platform execution path that joins:

1. a Windows/Linux node runtime;
2. authenticated remote task transport over the mesh;
3. a sandboxed compute worker;
4. resource discovery that includes CPU, RAM, GPU and accelerator capabilities;
5. model/artifact distribution;
6. result verification and durable receipts;
7. explicit owner-controlled resource grants.

The current system registry records transport, archive, hardware-model and node-manifest contracts, but the inspected integration-gap registry contains no canonical compute-job, compute-resource, model-artifact or compute-result contract. This is the highest-priority federation-level gap.

This is a documentation/source inspection, not a fresh local build or execution of the recorded tests. No production-readiness claim is made.

## 2. Repositories and actual responsibilities

### 2.1 Canonical architecture root — `Shtenco/synergy_system`

The repository is the federation governance and contract root, not the network daemon, AI runtime, ledger or OS kernel.

The README's 2026-09-29 snapshot reported 75 repositories, 39 contract families and 44 runtime adapter edges, with 0 E2E-tested edges and 0 deployed edges. The newer `registry/REPOSITORY_INTERFACES.json` is dated 2026-11-20 and reports 77 repositories. The newer `registry/INTEGRATION_GAPS.json` (2026-11-20) reports 39 registered contracts, 0 missing endpoints among those registered contracts, 44 runtime adapter edges, 0 E2E-tested edges, 2 uncontracted candidates and 3 observed contract risks. The `CONTRACT_REGISTRY.json` remains dated 2026-09-29 with 39 contract families. These snapshots must not be collapsed into one date or treated as a complete current runtime inventory.

A zero missing-endpoint count only means that the listed contracts have declared producer/consumer endpoints. It does not mean every relevant subsystem has a contract: no compute-job, compute-resource, worker-lease, model-artifact, execution-receipt or independent-compute-verification family appears in the 39-entry contract registry. Adapter presence must not be confused with observed cross-repository execution.

The two currently named uncontracted candidates are the hierarchical cognitive-memory subsystem (proposed `synergy.memory.context/v1`) and the Autopilot mission-lifecycle subsystem (proposed `synergy.agent.mission-lifecycle/v1`). They are separate integration gaps and must not be treated as substitutes for a compute execution contract. The three observed risks in the November gap registry concern payment-settlement lifecycle, financial outbox authenticity/concurrency, and agentic-economy accounting correction/replay. These are relevant federation trust/economic blockers, but none is a compute-worker authorization or reward contract.

Relevant canonical files:
- `registry/REPOSITORY_INTERFACES.json`
- `registry/INTEGRATION_GAPS.json`
- `registry/DEPENDENCY_GRAPH.json`
- `registry/CONTRACT_REGISTRY.json`
- `registry/SECURITY_BLOCKERS.json`

### 2.2 Network — `Shtenco/synergy_net`

The README defines SynergyNet as a post-quantum P2P mesh/content-transport layer and describes a target pipeline for framing, content addressing, deduplication, compression, protected sessions, multipath routing and relay/store-and-forward.

The first milestone in the README is a local 3–10-node testbed. The README explicitly treats performance as a hypothesis until measured.

The repository already exposes the federation contract `synergy.transport.evidence/v1` through:
- `runtime/synergy_contracts.py`
- `tests/test_synergy_contracts.py`

Its registry status is ADAPTER_INTEGRATED, but this is not proof of a deployed cross-platform mesh.

### 2.3 PQ mesh and agent fabric — `Shtenco/synergy_ai_blockchain`

This repository is more advanced than the original SUMI v2 document assumed. Its main branch contains substantial Rust source and evidence for PQ mesh and agent-fabric work.

#### P6 — PQ Mesh Internet

Evidence anchor: `evidence/p6_pq_mesh/P6_STATUS.json`.

The recorded P6 result includes:
- logical mesh addresses derived from PQ identity;
- link-state routing, loop rejection, hop limits and replay/downgrade protection;
- end-to-end and per-hop encryption;
- ML-KEM-1024 key exchange;
- ML-DSA-87 / SLH-DSA-SHAKE-256s identity authorization;
- a recorded 3-node TCP relay smoke;
- 24/24 mesh tests and a recorded 329/329 default regression run.

Explicit P6 limitations in the evidence:
- the 3-node TCP smoke used one physical host;
- a second independently controlled physical/VM host is required for WAN cross-host evidence;
- production Windows Wintun and Linux TUN adapters were not packaged in the recorded commit;
- PQ protection ends at the mesh exit node unless the destination protocol separately protects traffic.

The P6 feature branch is 46 commits behind main and 0 commits ahead. Treat P6 as historical evidence whose code appears to have been incorporated into main; verify the exact current main source and tests before changing it. Do not merge the stale branch over main.

#### P7 — Node Commander + Agent Fabric

Evidence anchor: `evidence/p7_agent_fabric/P7_STATUS.json`.

The recorded P7 result includes:
- local swarm scheduler;
- role/tool/resource matching;
- local-first placement;
- task leases and expiry;
- deterministic failover;
- task commitments and execution receipts;
- replay consumption;
- PQ-authorized receipts;
- independent verifier binding;
- reward replay protection.

The recorded test report lists core, adversarial, reference-PQ and Node Runtime checks as passing. These are recorded results, not independently rerun in this audit.

P7 explicitly lists remaining gates:
- actual remote agent execution and result-return transport over PQ-MESH;
- production sandboxing with Windows Job Objects and Linux namespaces/cgroups/seccomp;
- per-task filesystem/network/secret isolation;
- authenticated HTTP and PQ-MESH MCP gateway;
- node-scoped capability tokens and human approval for dangerous tools;
- three-independent-device distributed swarm evidence.

The P7 feature branch is 24 commits behind main and 1 commit ahead. The only ahead-of-merge-base file reported by GitHub compare is `node-runtime/crates/synergy-node/src/bin/agent-fabric-stdio.rs`. The shared agent-fabric library is present on main at `node-runtime/crates/agent-fabric/src/lib.rs`. Review the one-commit delta and port only what remains needed; do not merge the stale branch wholesale.

The inspected scheduler data model currently describes CPU millis, memory, tools and local/remote placement. It does not yet describe GPU memory, accelerator backend, model residency, bandwidth-aware partitioning or real remote execution. The current scheduler is a useful control-plane foundation, not yet a heterogeneous AI compute fabric.

### 2.4 Node orchestration — `Shtenco/synergy_meta_os`

The README defines Meta-OS as the service orchestrator and explicitly separates it from `synergy_system` (architecture/governance) and `synergy_net` (data plane).

The current compatibility runtime is `runtime/orchestrator.py`; tests include `tests/test_orchestrator.py`. It verifies declared roles/capabilities, artifact SHA-256, path confinement and resource limits, and records staged activation/rollback behavior.

Important platform limitation: the inspected runtime imports Python's `resource` module and explicitly describes itself as targeting conventional Linux during development. It is not a Windows-native runtime. Windows Job Objects and a platform-specific process/resource adapter remain necessary. The current known role/capability schema also needs a bounded compute-worker capability family; do not simply grant generic `agents.execute` broader host access.

### 2.5 Host substrate — `Shtenco/synergy_turbo_linux`

The current README positions TURBO Core as an x86-64 systems research laboratory with bounded operations, capability checks, fixed-capacity queues and reproducible microbenchmarks. Windows-to-VPS orchestration is described as a separate historical investigation.

It is not a ready-made Windows/Linux cross-platform runtime and should not become the sole SUMI host requirement. SUMI must first work on conventional Windows and Linux; TURBO can be an optional hardened host/backend.

### 2.6 NEXUS — `Shtenco/synergy_gllm_nexus`, `synergy_agi_nexus`, `synergy_agi_olga`

The NEXUS repository contains extensive research, frozen benchmark protocols and model artifacts. The system interface registry classifies `synergy_gllm_nexus` as DOCUMENTATION_ONLY for federation runtime integration. `synergy_agi_nexus` is the canonical NEXUS architecture/core; `synergy_agi_olga` is a historical research lineage and benchmark-generation source.

These repositories should supply model selection and scheduling intelligence through a versioned proposal interface. They should not be assumed to provide a production distributed inference transport or compute worker.

AI scheduling must remain advisory and bounded by deterministic policy. A deterministic fallback scheduler is mandatory.

### 2.7 Compression and model artifacts

Canonical compression repository found in the federation registry: `Shtenco/synegy_ai_compress`.

It already provides `synergy.archive.evidence/v1` and adapters to SynergyNet and Meta-OS. The SynergyNet README still refers to `Shtenco/ai_compress`; documentation must be normalized to the canonical repository after confirming ownership and source provenance.

Additional relevant repository:
- `Shtenco/synergy_gguf_compress`: GGUF/LLM compression research; the federation registry classifies current main as DOCUMENTATION_ONLY. Do not treat it as a production model distribution engine.

Lossless archive compression must be benchmarked separately from model quantization, GGUF conversion and tensor compression. These have different correctness and quality contracts.

### 2.8 Additional repositories missing from the original 14-repository list

The canonical 75-repository atlas identifies further relevant systems:
- `synergy_agentic_ai_economy`: agent task/contract/market simulation; currently has `synergy.agent.economy-simulation/v1`, not a compute execution protocol.
- `synergy_motherboard_xpu_xml`: hardware/XPU model contract consumed by Meta-OS; useful as an inventory input, not proof of runtime accelerator discovery.
- `synergy_post_quantum_radio`: conceptual physical transport; no implementation should be assumed from its name.
- `synergy_messenger`: communication client surface; registry marks NEEDS_HARDENING.
- `synergy_apps`: master application/presentation layer.
- `synergy_gguf_compress`: model-format research.

These repositories should be included in SUMI's dependency map where relevant, but not all should become core runtime dependencies.

## 3. Current integration state

The inspected registry already has these relevant contracts:
- `synergy.transport.evidence/v1`: SynergyNet → Meta-OS and PQ blockchain.
- `synergy.archive.evidence/v1`: AI Compress → SynergyNet and Meta-OS.
- `synergy.runtime.node-manifest/v1`: Meta-OS → Turbo Linux.
- `synergy.runtime.hardware-model/v1`: XPU hardware model → Meta-OS.
- `synergy.trust.commitment/v1`: PQ blockchain → MetaChain.

The inspected `INTEGRATION_GAPS.json` contains no canonical contract family for:
- compute resource advertisement;
- compute job submission/lease;
- remote execution authorization;
- model artifact manifest/distribution;
- execution result/receipt;
- independent compute verification;
- compute reward eligibility.

This gap should be closed before cross-repository implementation spreads.

## 4. Proposed SUMI contracts (design proposal; not yet registered)

Create versioned contracts under `synergy_system` and corresponding producers/consumers only after schema review:

1. `synergy.compute.resource-profile/v1` — signed, privacy-minimized resource advertisement (CPU, RAM, GPU/accelerator, runtimes, quotas, availability, network class).
2. `synergy.compute.job/v1` — immutable task manifest (input/model hashes, runtime, limits, privacy, budget, expiry, retry and verification policy).
3. `synergy.compute.lease/v1` — exclusive bounded assignment with epoch/expiry, worker identity and replay protection.
4. `synergy.model.artifact/v1` — model identity, architecture, format, version, hashes, license/provenance, runtime compatibility and access policy.
5. `synergy.compute.execution-receipt/v1` — worker-signed execution statement bound to exact job, lease, model, inputs, output and runtime.
6. `synergy.compute.verification/v1` — independent verifier/challenge result; worker must not self-verify rewarded work.
7. `synergy.compute.reward-eligibility/v1` — evidence-only eligibility input for the authoritative economic layer; it must not directly mint or settle funds.

Contract authority boundaries:
- Meta-OS owns node/service capability grants and lifecycle.
- SynergyNet owns transport and delivery evidence.
- Agent Fabric owns job/lease orchestration primitives.
- Compute Worker Runtime owns sandboxed execution.
- Model registry owns model artifact identity/provenance.
- Independent verifier owns execution validation.
- Blockchain owns immutable trust commitments and replay protection.
- Financial OS remains the canonical accounting authority.
- Payment system remains settlement authority.

## 5. Required architecture correction

Do not make `synergy_net` the owner of the compute scheduler or execution runtime. Keep the layers separate:

```text
synergy_system
  └─ versioned contracts, authority and dependency registry

synergy_meta_os
  └─ node lifecycle, capabilities, resource policy, service supervision

synergy_net
  └─ authenticated transport, peer routing, relay, artifact/result delivery

synergy_ai_blockchain
  ├─ PQ mesh primitives and trust commitments
  ├─ Agent Fabric scheduler/leases/receipts
  └─ verifier/reward evidence primitives

Compute Worker Runtime
  └─ Windows/Linux platform adapters + sandbox + CPU/GPU execution

NEXUS
  └─ bounded placement/scheduling proposals; deterministic fallback

AI Compress / GGUF research
  └─ artifact storage, dedup, compression and format-specific tools
```

A separate new repository is not yet justified. First determine whether the Compute Worker Runtime belongs in the existing `synergy_ai_blockchain/node-runtime` workspace or as a clearly bounded crate/service under Meta-OS. Keep platform adapters separate from portable job and receipt schemas.

## 6. Prioritized implementation gates

### Gate 0A — Freeze and reconcile existing code
- Compare P6/P7 branch heads to current main.
- Record exactly which P6/P7 files are already in main.
- Preserve the P7 stdio adapter as a reviewable one-commit delta.
- Do not merge the stale P6/P7 branches wholesale.
- Verify current main test commands and evidence paths.

### Gate 0B — Cross-platform runtime design
- Split portable orchestration policy from OS-specific process control.
- Linux backend: namespaces, cgroups, seccomp and filesystem/network isolation.
- Windows backend: Job Objects, restricted tokens/AppContainer where appropriate, ACL and firewall policy.
- Define a common capability and resource-limit contract.
- Add Windows CI and Linux CI before declaring cross-platform support.

### Gate 0C — Remote compute path
- Authenticated peer registration over PQ-MESH.
- Submit job → acquire lease → fetch verified input/model → execute sandboxed → return output → independently verify → consume receipt once.
- Add a 3-independent-device test across at least two physical hosts.
- Inject worker loss, route loss, lease expiry, duplicate result and replay.

### Gate 0D — Heterogeneous resource profile
- Add GPU vendor/backend and VRAM, accelerator capability, model/runtime compatibility, bandwidth and availability policy.
- Keep private hardware details opt-in and minimized.
- Begin with CPU-only jobs; add GPU after deterministic CPU worker flow passes.

### Gate 0E — AI model execution
- Start with replicated model inference on independent nodes.
- Then implement pipeline parallelism only where measured network bandwidth/latency makes it useful.
- Treat tensor/expert parallelism as later research, not MVP acceptance criteria.
- Add model artifact signatures, hashes, license/provenance and exact runtime pinning.

## 7. Explicit non-goals for the first MVP

- No token incentives or Proof-of-Compute minting.
- No arbitrary untrusted shell execution on volunteer machines.
- No requirement that every node expose a public port.
- No assumption that mesh relays can decrypt application payloads.
- No claim that several computers automatically make one GPU or one memory pool.
- No tensor-parallel distributed inference over high-latency consumer Wi-Fi as a default.
- No production security claim from local unit tests alone.

## 8. Evidence required for promotion

Each gate must preserve:
- exact repository and commit SHA;
- exact build/test command;
- OS and hardware profile;
- raw test output and exit code;
- input/model hashes;
- task/lease/receipt identifiers;
- failure-injection results;
- CI run URL or explicit absence;
- known limitations.

Maturity labels:
- `SOURCE_PRESENT`
- `UNIT_TESTED`
- `LOCAL_RUNTIME_VERIFIED`
- `CROSS_HOST_VERIFIED`
- `CROSS_PLATFORM_VERIFIED`
- `INDEPENDENTLY_AUDITED`
- `PRODUCTION_CANDIDATE`

Do not promote an item by documentation-only evidence.

## 9. Audit limitations

This Phase 0 pass inspected repository metadata, selected READMEs, the system interface/dependency/integration registries, selected source files, P6/P7 evidence JSON and branch comparisons. It did not inspect every file in all 75 repositories, run a local build, execute Windows/Linux workloads, independently reproduce P6/P7 tests, or perform a cryptographic audit.

The next audit pass must inspect the complete source/test/build surfaces for:
- `synergy_net`;
- `synergy_meta_os`;
- `synergy_ai_blockchain` (main plus P7-only delta);
- `synergy_turbo_linux`;
- `synergy_gllm_nexus`;
- `synegy_ai_compress`;
- `synergy_motherboard_xpu_xml`;
- `synergy_agentic_ai_economy`.

**Conclusion:** SUMI should proceed by integrating and hardening the existing P6 mesh and P7 agent-fabric foundations, adding a genuine Windows/Linux compute worker and remote execution path, and registering explicit compute/model/evidence contracts in the system federation. The first decisive milestone is a verified task executed across three independently controlled devices—not a new directory tree or another architecture-only README.
