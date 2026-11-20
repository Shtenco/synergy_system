# Memory, archive and mission boundary audit — 2026-11-20

## Scope and evidence

Focused live source review of the exact branch heads below:

- `synergy_ai_coder`: `feat/recursive-context-archive-integration-20261118` — `ef6b0911337610773d3915ed93431ed98c897e6e`
- `synergy_long_term_harness`: `feat/company-autopilot-memory-v1` — `bdc26413d886fb026bdc22c3a6f76dc2df873a1c`
- `synergy_hierarchical_cognitive_memory_architecture`: `feat/hierarchical-cognitive-memory-v1` — `6a55da91afafa27a005dd662617696b890ae5955`

The main branches of Long Term Harness and Hierarchical Cognitive Memory are README-only in the inspected snapshot. Their implementation evidence is on non-main branches, so those repositories remain `ARCHITECTURAL_ONLY` in the canonical runtime registry until the code is merged, tested and integrated.

## Functional boundary comparison

| Capability | AI Coder archive | Long Term Harness | Hierarchical Cognitive Memory |
|---|---|---|---|
| Primary role | Engineering agent's durable context archive and semantic-memory interchange | Long-horizon agent harness, memory store and durable mission control | Provider-independent hierarchical knowledge/RAG memory |
| Persistence | Append-only SQLite archive, L0-L5 lineage, digest checks, byte archive | SQLite chunk store, compressed content-addressed chunks, manifest digest | SQLite versioned records, graph edges, source snapshots, embeddings, system-core history |
| Retrieval/context | Archive search preview, restore original L0 source, semantic-memory adapter | Namespace search, bounded context bundle, exact full hydration or marked preview truncation | Budgeted context planning, lexical/exact/vector/graph retrieval, trust ranking |
| Safety/integrity | SHA-256, source lineage, credential redaction in semantic-memory interchange; namespace is not authorization | SHA-256, bounded decompression, namespace validation, context data explicitly untrusted | Value hashes, trust labels, source revision/hash provenance, token-budget planner |
| Mission lifecycle | Engineering planning/review/release runtime, requirement/change evidence contracts | Durable mission ledger, idempotency, fencing epochs, approval and signed external verification | Not a mission orchestrator; provides knowledge memory and system-core history |
| Existing typed boundary | `synergy.engineering.requirement-trace/v1`, `synergy.engineering.change-evidence/v1`; not a memory interchange contract | No canonical cross-repository runtime contract registered | No canonical cross-repository runtime contract registered |

## What overlaps and what does not

There is genuine functional overlap in durable source retention, append-only/versioned records, content hashes, namespace separation, SQLite persistence and bounded retrieval into a finite model context.

There are also distinct authorities that should not be collapsed:

1. **AI Coder** owns engineering workflow artifacts: requirements, changes, checks, review and release evidence. Its memory/archive code is a subsystem for that workflow, not the federation's universal knowledge store.
2. **Long Term Harness** owns mission lifecycle concerns: mission submission, capability policy, lease/fencing, idempotency, approvals, execution receipts and long-horizon provider routing. Its `missions.py` is not a replacement for the memory graph.
3. **Hierarchical Cognitive Memory** owns the general knowledge-memory model: keyed/versioned records, trust, source provenance, graph edges, embeddings, context budget and system prompt core history. It is not the mission authority and should not become a business-action executor.

The modules reviewed are different implementations and data models; this pass did not establish byte-identical code between these three memory-oriented repositories. It establishes semantic overlap and an interface gap, not a duplicate-repository verdict.

## Canonical registry cross-check

- `synergy_ai_coder` is already `ADAPTER_INTEGRATED` for engineering requirement/change evidence. That status applies to the engineering evidence contracts, **not** to its context archive or semantic memory.
- `synergy_long_term_harness` remains `ARCHITECTURAL_ONLY` because its main branch does not yet contain the inspected implementation and no canonical cross-repository mission/memory contract is registered.
- `synergy_hierarchical_cognitive_memory_architecture` remains `ARCHITECTURAL_ONLY`; its main branch is README-only and no canonical memory contract, producer/consumer adapter or E2E path is proven.

No change to the canonical contract registry is justified in this pass. Do not invent a memory contract ID or mark an adapter integrated before payload schemas, authority, producer/consumer ownership, compatibility rules and executable tests exist.

## Recommended integration plan

1. Keep all three repositories independent; do not merge them into one memory monolith.
2. Define a narrow **Memory Record Interchange** contract for content-addressed source records: record ID, namespace, kind, schema/version, source reference/revision, payload hash, trust/evidence metadata, parent links and retention/restore semantics.
3. Define a separate **Context Retrieval Request/Result** contract: task/query, selected model profile, token budget, selected record IDs and hashes, trust filtering, omissions, warnings and exact provenance.
4. Define a separate **Mission Lifecycle** contract for mission ID, idempotency key, capability, role, approval state, lease/fencing epoch, result digest and verifier receipt. Keep financial/external actions behind explicit policy gates.
5. Treat memory as untrusted evidence. Authorization must be enforced by the owning runtime; namespace filtering alone is not access control.
6. Add producer/consumer conformance tests, adversarial namespace/tenant tests, digest/tamper tests, restore tests, bounded decompression tests, prompt-injection tests, and cross-process restart tests.
7. Add one E2E harness that proves AI Coder can request relevant memories, Long Term Harness can persist and resume a mission, and the selected memory provider can return provenance-verified context under a fixed token budget. The test must exercise the actual adapters, not merely instantiate each package.
8. Only after those tests are green should the interface registry promote the corresponding edges from `ARCHITECTURAL_ONLY` / contract-defined to `ADAPTER_INTEGRATED` and eventually `E2E_TESTED`.

## CI and branch status

The inspected AI Coder feature branches have substantive code, but their PR workflows failed before any step (runner ID 0, empty steps). Two reruns were accepted but remained queued at the last check; older Midas/Science workflows could not be rerun because GitHub's one-month retry window had elapsed. Long Term Harness PR CI was also observed to fail before test steps. These are CI evidence blockers, not proof that the code tests fail.

## Decisions

| Repository | Decision | Reason |
|---|---|---|
| `synergy_ai_coder` | DEVELOP | Keep engineering authority; finish archive integration tests and exact-head CI |
| `synergy_long_term_harness` | DEVELOP | Keep mission authority; merge/validate implementation and define mission boundary |
| `synergy_hierarchical_cognitive_memory_architecture` | DEVELOP | Keep general memory authority; define typed provider API and provenance/E2E tests |
| Shared memory provider runtime | Not created | Avoid mandatory coupling and preserve independent deployment |
| MERGE-READY | None | Exact-head green CI and E2E contract closure are absent |
| ARCHIVE-CANDIDATE | None | These are complementary active responsibilities, not redundant repos |

