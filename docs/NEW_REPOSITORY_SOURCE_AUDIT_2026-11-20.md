# Newly Inventoried SYNERGY Repositories — Targeted Source / Branch / CI Audit

**Snapshot:** 2026-11-20  
**Scope:** 12 of the 17 repositories added in the November owner-inventory refresh. Five additional repositories had already received targeted audits in the earlier v1.4–v1.6 audit waves.  
**Method:** current main tree and README, selected implementation branches, tests/workflows, open-PR map and exact workflow runs.  
**Mutation policy:** no child repository branches, source files, PRs or deployments were changed. Findings below do not promote any component to production or E2E status.

## Executive result

The 12 repositories below are now source/branch inspected. Their maturity remains provisional until the full README passport, reproducibility and integration evidence gates are closed.

| Repository | Main HEAD (abbreviated) | Branches | Open PRs | Evidence result |
|---|---|---:|---:|---|
| synergy_complex_matrix_multiplication | 077ce326b203 | 1 | 0 | Substantial experimental code/results; no CI workflow in main; V11 end-to-end gate not closed |
| synergy_search_engline | 8e3c6cd42c47 | 1 | 0 | HardNAV / triangular-economy simulator, not a search engine; no CI or tests in main |
| synergy_lead_search_engline | 5654e37fdc34 | 3 | 2 | Offline Lead OS; exact-main CI green, 14 tests passed; not deployed |
| synergy_triangle_money_system | 8fb8a604a225 | 9 | 8 | Foundry simulation and tests; latest main CI failed; all 8 PRs are drafts |
| synergy_ai_llm_rwkv | 5f5d2a44610e | 2 | 0 | Main weight-mirroring workflow failed; quantizer exists only on feature branch and is not full-model validated |
| synergy.github.io | 4d1b67fd00c4 | 3 | 1 | Static presentation/frontend surface; not an authoritative backend |
| synergy_meta_api | 1f208b6b581d | 2 | 1 | Main is README-only; integration branch has local FastAPI/MCP prototype; CI failed |
| synergy_ai_workspace | 7540ad8f565a | 11 | 2 | Main is README-only; desktop implementation is on release branch; RC CI failed |
| synergistic_economics | 7e9e5579ccb0 | 19 | 13 | Extensive research/prototype corpus; five integration-branch validation workflows passed on exact branch SHA; still R&D |
| synergy_metaverse | a27d820bac90 | 10 | 5 | Main is README + one NMEA test; selected platform branch is documentation/catalogue only; no runtime evidence |
| synergy_maps | 9292be3e8614 | 10 | 9 | Main is README-only; Overture/Cesium implementation exists on work branches; latest selected branch CI failed |

## Repository-level findings

### 1. Complex Matrix Multiplication / Q-CNO

Main contains 112 blobs, extensive Python source, result CSV/JSON files and scientific reports. There is no GitHub Actions workflow in the inspected main tree.

The current V11 verified report explicitly says the hard end-to-end gate is not closed. The deep learned basis remains worse than the PCA quality oracle; the current PyTorch staged implementation is slower than the dense basis at N=512; the best canonical active-gate wall-clock gain is 6.83x. Earlier apparent 100x–300x multithread results were rejected after single-thread controls showed BLAS dispatch/thread overhead. PPL(student)/PPL(teacher) <= 1.05, >=8x total compression and >=100x end-to-end speed are not verified.

**Status:** active research; do not describe as quantum advantage, production accelerator or end-to-end 100x speedup.

### 2. synergy_search_engline

The main README and source identify this as **HARDNAV Multiplier / Triangular Non-Inflationary Economy**, not a search/retrieval engine. Main contains a Solidity lab contract, mathematical notes and Python simulation/optimizer files, but no tests or CI workflow were found in the main tree.

Its own test-results and assumptions documents label the multiplier values as simulated. The model assumes an independent external edge, recurring capacity and cost assumptions; competition, edge half-life, missed fills, latency, bridge risk, gas volatility and inventory imbalance remain unmodelled or incomplete.

**Status:** R&D simulation. Correct its system-registry domain from INTELLIGENCE_AGENTS to BLOCKCHAIN_MONETARY; do not infer live arbitrage or realized HardNAV from simulated multipliers.

### 3. Lead Search Engline / Lead OS

Main contains a Python package, FastAPI service, SQLite/FTS5 store, offline import, human-review flow and approval-gated CRM outbox. The exact main SHA passed workflow run 40054962494: **14 tests passed**, compileall succeeded, one deprecation warning.

Two PRs are open: #2 ready-for-review and #1 draft. The README correctly states this is an offline candidate, not a deployed lead-discovery service. External crawling, the full historical SMM archive, production CRM dispatch and calibrated V7 learning-to-rank are not established by this main-branch evidence.

**Status:** working offline candidate / R&D, not STUB_SPEC_ONLY and not production.

### 4. Recursive Collateral Money System / Triangle Money

Main contains Solidity contracts, a Foundry test suite and a Python numerical model. The tests cover synthetic accounting invariants, initial HardNAV, mint not creating HardNAV, external revenue accounting and modelled liquidity multipliers.

The latest exact-main workflow run 42536884266 failed. GitHub returned BlobNotFound for the job logs, so the cause is **unknown**; earlier October runs succeeded but do not override the latest main result. Eight open PRs are all draft.

The 2.166x / 2.556x headline figures are productive-liquidity / collateral-capacity multipliers under the model assumptions, not an increase in HardNAV and not realized external profit.

**Status:** simulation / EVM lab; latest main CI red, no live market or production deployment evidence.

### 5. RWKV-7 quantization

Main contains the original-weight mirroring workflow and documentation; the main workflow run 39465033459 failed. The quantization implementation is on feature branch feature/rwkv7-original-weights, not main.

That branch contains a weight-only quantizer, packing/restore code and synthetic tests. The tests validate bit packing, round-trip shape/finite values, a small residual case, budget allocation and a tiny synthetic checkpoint pipeline. They do not validate the full 2.9B checkpoint, task-level PPL parity, a complete RWKV runtime or GPU speed. The bit allocator uses sampled weight reconstruction MSE rather than activation/task calibration. The 700 MB target is an archive-size budget, not a VRAM guarantee.

**Status:** experimental weight-conversion research; no quality-equivalent 700 MB model or inference acceleration claim.

### 6. synergy.github.io

Main contains a 228-blob static website and frontend surfaces. Its README explicitly separates the presentation layer from backend authority; same-origin calls without a backend return 503 / backend_not_configured. Static UI, forms and product cards do not establish deployed APIs or working finance/SMM services.

One draft PR is open. Published Pages execution was not independently re-verified in this pass.

**Status:** presentation/frontend candidate only.

### 7. META-API

Main contains only README documentation. Branch integration/meta-api-mcp-v0.1 contains 29 blobs, FastAPI/MCP source, policy, workflow/runtime modules and tests. PR #1 is draft. The latest branch CI run 39692897514 failed; logs were unavailable (BlobNotFound), so the failure cause remains unknown.

The branch describes a local prototype with a narrow read-only tool allowlist and explicit HTTP host/path configuration. It is not a production multi-tenant gateway; the documented DNS-rebinding/SSRF and authorization boundaries remain relevant.

**Status:** branch-only local prototype; no production gateway.

### 8. AI Workspace

Main contains only README. The release/v1.0-desktop-rc branch contains 218 blobs, Python workspace modules, Tauri shell, local service, tests and release workflows. Two PRs are draft. The exact release-branch source-validation run 39771092264 failed; logs were unavailable (BlobNotFound).

The documented design uses a local 127.0.0.1:8129 control plane, SQLite WAL and human approval. External action execution is fail-closed when a verified provider adapter is absent. Windows NSIS release and full GUI E2E are not established.

**Status:** implementation is branch-scoped; main is documentation-only; release candidate not qualified.

### 9. Synergistic Economics

Main contains 84 blobs, a large research corpus and validation workflows. The integration/economic-core-consolidation-2026-11-13 branch contains 207 blobs. Five workflows passed on its exact HEAD 8ba881bf30ea: prototype validation, schema validation, SCCE Stage-C2 validation and audit-control checks.

Thirteen PRs are open (12 draft, one ready). Green research/prototype validation is evidence for those exact suites and that branch SHA; it is not proof of a deployed economic operating system, production ledger, live settlement or institutional adoption.

**Status:** substantial R&D / simulation and prototype programme; not production.

### 10. Metaverse

Main contains only README and one NMEA test. The selected work/global-world-platform-foundation-20261116 branch contains 11 blobs, primarily architecture, data-governance, coverage and research-catalogue documents; no executable spatial runtime or CI workflow was found on that branch. Five PRs are draft.

**Status:** architecture/research catalogue, not a deployed metaverse or spatial platform.

### 11. Maps

Main contains only README. The work/overture-global-divisions-ingest-20261116 branch contains TypeScript/Cesium sources, Python Overture ingestion and tile-planning scripts, tests and a CI workflow. The workflow covers npm tests, Python unittest, py_compile and npm build.

All nine open PR head branches have latest visible workflow runs with conclusion=failure. The selected run 44338339348 also failed; GitHub job logs returned BlobNotFound, so exact causes remain unknown. All nine PRs are draft, with a stacked branch chain from planner → resumable runner → Overture ingestion → Cesium rendering → EAEU coverage. The implementation has not been merged to main.

**Status:** branch-level implementation candidate; main remains README-only; CI currently red on the inspected branch.

## Five additions with earlier audit evidence

The remaining five newly inventoried repositories already have targeted findings in earlier audit waves:

- **synergy_computing_topology:** substantial C/Python/LLVM/kernel/benchmark source; benchmark claims are workload-specific, not OS-wide speedup; kernel load and cross-host execution are not established.
- **synergy:** umbrella governance root; 91-repository owner inventory, branch census and open-PR map are published separately from child runtime authority.
- **synergy_ai_economic:** documentation/research simulation, not an executable validated digital twin.
- **shtenco_micro_ai:** downloader/query/benchmark tooling; model weights remain external; latest main inference workflow failed with unavailable logs.
- **synergy_long_term_harness:** main is README-only; implementation and tests are on non-main branches; draft PR and CI evidence remain unresolved.

## Registry implications

1. Keep all 16 additions provisional until their repository-specific README passports, reproducibility and integration evidence are complete.
2. Correct the SYNERGY SYSTEM domain for synergy_search_engline to BLOCKCHAIN_MONETARY; its current README is a HardNAV/triangular-economy simulator, not a search engine.
3. Reclassify synergy_lead_search_engline from STUB_SPEC_ONLY to RND: main contains executable offline code and tests, and exact-main CI passed; deployment remains unproven.
4. Keep synergy_maps, synergy_meta_api and synergy_ai_workspace as main-branch documentation/stub surfaces while explicitly recording their branch-only implementations and CI status.
5. Do not promote any of these nodes to E2E_TESTED or DEPLOYED based solely on branch existence, green unit tests or research documentation.


## Additional targeted source audit — cognitive memory repository

`Shtenco/synergy_hierarchical_cognitive_memory_architecture` is the 92nd owner repository and the 17th November-added repository. Its main branch remains README-only; feature PR #1 contains the implementation (80 commits, 25 files, 1,538 additions). The feature includes L0 core, budgeted context retrieval, L2 FTS5/graph/vector retrieval, L3 content-addressed provenance and repository ingestion. Source inspection identified three unresolved promotion/security concerns: unauthenticated local API, no explicit symlink rejection/path-containment check in ingestion, and URI-only source identity that can collide across repositories. Latest CI was cancelled with no executed steps. It remains `CANDIDATE / PENDING deep README passport`, not an integrated runtime component.
