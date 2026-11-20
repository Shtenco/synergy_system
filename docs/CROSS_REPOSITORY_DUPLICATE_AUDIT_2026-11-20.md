# Cross-repository functional duplication and CI evidence audit — 2026-11-20

## Scope and method

This is a focused, source-backed pass over nine active trading/runtime repositories. It is not yet a claim that all 92 repositories have been compared file-by-file. Git Trees were read from each repository's `main` at the SHAs listed below. Paths under `src/<package-name>/` were normalized to `src/PACKAGE/`; Git blob SHA equality was used as an exact-content test. Similar path names alone were not counted as duplicates.

## Executive finding

Seven separately named trading products share a highly repeated enterprise/runtime scaffold. Across the 21 pairs in the initial seven-repository matrix:

- each pair has 63–65 common normalized file paths;
- each pair has 29–30 byte-identical Git blobs;
- 17 identical files per pair are in the common enterprise/runtime/test/CI foundation;
- product core modules and product contract modules differ, and each product declares a distinct contract/authority.

This is a confirmed shared-code duplication pattern, not proof that the seven product domains are interchangeable.

## Product boundaries and decisions

| Repository | Main SHA | Product contract | Authority | Decision |
|---|---|---|---|---|
| `synergy_market_maker` | `3edcea187c45866d55a65b74dc707b7b1009a69b` | `synergy.trading.liquidity-quote/v1` | `market_making` | KEEP |
| `synergy_adaptive_engine` | `c4af6194eedfbf9b9c0824822abe42306ba9f6b8` | `synergy.trading.market-regime/v1` | `adaptive_policy` | KEEP |
| `synergy_riskguard` | `bc3ef1810c5d77f54b8a9ecf2f1b8adc35231f2b` | `synergy.trading.risk-decision/v1` | `trading_risk` | KEEP |
| `synergy_trademux` | `fe584afeba1410f40640672f277be4ab16e76b8c` | `synergy.trading.execution-plan/v1` + `execution-result/v1` | `trade_execution` | KEEP |
| `synergy_relative_value` | `0f37ef55ac989933acd63a0954b5cf521eec4449` | `synergy.trading.relative-value-signal/v1` | `relative_value_research` | KEEP |
| `synergy_midas_institutional` | `75f646380cd0a1478e5093216615b1af8ded1fbf` | `synergy.trading.institutional-assessment/v1` | `institutional_research` | KEEP |
| `synergy_marketvision` | `1baf9fa65c9974bb241f3a4fb2a352424bfe9bcc` | `synergy.trading.market-features/v1` | `market_perception` | KEEP |
| `synergy_ai_investment_committee` | `7dbec0202badf1afce60ada83b5402f8d8ed9f14` | `synergy.trading.investment-thesis/v1` | `investment_committee` | KEEP |
| `synergy_quantlab` | `57ee40a6879c0db6550b573aacadad27347fb2db` | `synergy.trading.validation-decision/v1` | `trading_validation` | KEEP |

The distinct contracts are evidence that the intended product responsibilities differ: quoting, regime adaptation, risk authorization, execution routing, relative-value signals, institutional assessment and market perception. Do not merge these product cores merely because their delivery scaffolding is similar.

## Exact pairwise duplicate matrix

Each cell is `common normalized paths / identical blob SHAs`.

| | Adaptive | Riskguard | Trademux | Relative value | MIDAS institutional | Marketvision |
|---|---:|---:|---:|---:|---:|---:|
| Market maker | 65 / 29 | 65 / 30 | 63 / 30 | 65 / 29 | 65 / 29 | 63 / 29 |
| Adaptive engine | — | 65 / 29 | 63 / 29 | 65 / 30 | 65 / 30 | 63 / 30 |
| Riskguard | — | — | 63 / 30 | 65 / 29 | 65 / 29 | 63 / 29 |
| Trademux | — | — | — | 63 / 29 | 63 / 29 | 65 / 29 |
| Relative value | — | — | — | — | 65 / 30 | 63 / 30 |
| MIDAS institutional | — | — | — | — | — | 63 / 30 |

Representative identical shared files include the CI workflow, enterprise adapter implementations for Bybit/CCXT/MT5, enterprise auth/audit/metrics/models/resilience/service modules, SQL audit table definitions, load-test harnesses, and parts of the acceptance tests. The two-repository deep check of market maker vs adaptive engine found 29 identical blobs across 65 common normalized paths; `core.py`, API, product logic and product contract are not identical.



### Nine-way common-code intersection

A second intersection check across all nine repositories confirms **63 normalized paths are present in every repository and 29 of those paths have the same blob SHA in all seven**. The 29-way identical set is:

- `.env.enterprise.example`, `.github/workflows/ci.yml`, `.gitignore`, `CHANGELOG.md`;
- `deploy/clickhouse/001_audit.sql`, `deploy/postgres/001_audit.sql`;
- `docs/AUDIT_DATA_MODEL.md`, `docs/ENTERPRISE_DEPLOYMENT.md`, `docs/LOAD_TESTS.md`, `docs/PRODUCT_STATUS.md`, `docs/RBAC.md`, `docs/SECURITY.md`;
- `loadtests/benchmark.py`, `loadtests/k6_smoke.js`;
- `src/PACKAGE/__init__.py` and the common enterprise package initializers, Bybit/CCXT/MT5 adapters, audit, auth, metrics, models, resilience and service modules;
- `tests/test_customer_demo.py`, `tests/test_enterprise_deployment.py`.

The nine `core.py`, `api.py` and `synergy_contracts.py` files each have **nine distinct blob SHAs**. This independently supports keeping the seven product domains separate while treating the enterprise scaffold as shared code to extract.

All seven product contract IDs are present in the central contract registry. Their producer/consumer implementation metadata is recorded, but the federation governance snapshot still reports **zero E2E-tested runtime edges**. Therefore registry presence and adapter declarations are not treated as proof of live end-to-end execution.



## API, contract and runtime topology cross-check

The central `REPOSITORY_INTERFACES.json` and `CONTRACT_REGISTRY.json` confirm that the seven repositories are not seven interchangeable copies. Their declared boundaries form this typed flow:

- `synergy_market_maker` → `synergy_midas_ai`: `synergy.trading.liquidity-quote/v1`.
- `synergy_adaptive_engine` → `synergy_midas_ai`: `synergy.trading.market-regime/v1`.
- `synergy_marketvision` → `synergy_midas_ai`: `synergy.trading.market-features/v1`.
- `synergy_relative_value` → `synergy_midas_ai`: `synergy.trading.relative-value-signal/v1`.
- `synergy_midas_institutional` → `synergy_midas_ai`: `synergy.trading.institutional-assessment/v1`.
- `synergy_riskguard` → `synergy_trademux`: `synergy.trading.risk-decision/v1`; Riskguard consumes `synergy.trading.validation-decision/v1` from `synergy_quantlab`.
- `synergy_trademux` → `synergy_pay_system`: `synergy.trading.execution-result/v1`; Trademux also owns the intra-repository execution-plan contract.

The five signal/research components converge into the MIDAS intelligence aggregator; the risk decision then gates execution routing, and the execution result flows to settlement. These are typed, registered, adapter-evidenced edges. They are not yet E2E-tested in the central governance snapshot (0 E2E-tested edges), so the architecture map must not present them as fully validated live flows.

## Architecture correction from the product-line V3 master specification

The source specification in `Shtenco/synergy_midas_institutional/docs/superpowers/specs/2026-09-21-final-product-line-3.0-master.md` explicitly requires independently deployable/licensable products and says there SHALL NOT be a mandatory shared runtime repository. Common concepts may be copied consistently across products. Therefore the initial suggestion to extract a shared mandatory runtime package is withdrawn: it would contradict the product-line architecture.

## Corrected architecture recommendation

1. Keep all nine product repositories and their domain-specific cores, API surfaces, contracts and independent release cycles.
2. Do not introduce a mandatory shared runtime dependency or centralize product execution.
3. Develop a versioned **Production Contract specification** covering auth, tenant/RBAC, authoritative control stores, idempotency, audit, readiness/liveness, observability, migrations and failure semantics.
4. Build a reusable **conformance test suite** that each repository runs locally/in CI against its own implementation; test behavior, not shared code identity.
5. Use code-generation/templates only for non-authoritative boilerplate where it does not create runtime coupling; generated files remain owned and released by each product.
6. Maintain a compatibility matrix and explicit versioned adoption status per repository. Security fixes propagate as reviewed per-repository changes.
7. Keep domain contract tests and add E2E tests at real producer/consumer boundaries. Registry declarations and matching adapter files do not prove runtime integration.

This resolves the exact-code duplication without violating independent deployment. The duplication is real; a shared runtime package is not the chosen remedy.










## Mission/task lifecycle overlap: Autopilot and Long-Term Harness

A branch-level comparison found a second functional overlap beyond memory storage:

| Capability | `synergy_agi_autopilot` Business Runtime | `synergy_long_term_harness` |
|---|---|---|
| Durable SQLite state | `TaskStore` with tasks and append-only events | `MissionStore` with missions and append-only events |
| Idempotency | Unique idempotency key; replay must match capability and params | Unique (company, key); replay must match a canonical fingerprint of capability, role and payload |
| Dispatch fencing | Conditional one-winner transition to running; uncertain tasks fenced | Worker/epoch lease; stale external lease moves to uncertain; completion must match current worker and epoch |
| Approval/policy | Capability registry, policy decision, approval and external-effects gate | Capability/role allowlist; external/financial actions gated; local bridge is no-network |
| Verification | Evidence verifier capability and task results | Result digest plus independent HMAC-signed verifier receipt, verifier must differ from worker |

These are **not identical implementations**. Autopilot owns the product's capability/policy/approval and external-effect runtime; Long-Term Harness owns mission-level lease epochs, result integrity and independent verification, as well as the memory archive. But they duplicate important lifecycle primitives: SQLite task state, idempotent replay, append-only events, execution claims and uncertain-outcome fencing.

**Decision:** KEEP both repositories; DEVELOP a shared, versioned mission lifecycle protocol (identity, idempotency, state machine, events, leases/epochs, uncertain outcomes, result digest and verifier receipt). Keep Autopilot's capability policy and Long-Term Harness's archive/verifier responsibilities local. Do not merge repositories or assume exactly-once external effects without provider reconciliation. Neither side currently has a registered cross-repository mission contract or E2E edge.

## Web and mobile surface duplicate spot checks

A separate exact-tree comparison covered four GitHub Pages repositories (`shtenco.github.io`, `shtencoauantai.github.io`, `synergychain.github.io`, `synergy.github.io`) and the two mobile app repositories:

- Across the six website pairs, common path counts range from 2 to 4 and the only identical blob is the shared `LICENSE` file between `shtenco.github.io` and `shtencoauantai.github.io`. No identical `index.html`, README or application asset was found. These are separate portfolio/research/central-platform surfaces, not a merge candidate on current evidence.
- `synergy_app` (Finance Android/iOS/web source, release verification) and `sinergy_super_app` (PWA/Android local mobile surface) share only the `README.md` and `LICENSE` paths, and neither blob is identical. Their release contracts are also distinct: `synergy.app.store-source-evidence/v1` vs `synergy.app.superapp-surface/v1`. Both accurately separate source verification from build/deployment authority. Decision: KEEP both; no repository merge. A future shared source-evidence schema fragment may reduce conceptual duplication, but should not collapse their platform-specific evidence.

### Mobile CI evidence

- `synergy_app` [run 42536928143](https://github.com/Shtenco/synergy_app/actions/runs/42536928143): `Verify store source` failed in ~3 seconds, `runner_id=0`, empty steps. Source verification tests were not evidenced as executed.
- `sinergy_super_app` [run 40031082442](https://github.com/Shtenco/sinergy_super_app/actions/runs/40031082442): `Build APK` failed in ~3 seconds, `runner_id=0`, empty steps. APK build was not evidenced as started.

Both are `BLOCKED_INFRA`, not evidence of failed source assertions or a failed APK compilation.

## Memory subsystem overlap: two candidates, complementary layers

A branch-level source comparison found overlapping memory primitives in two projects, but not identical products:

| Repository | Implemented branch-level responsibility | Distinctive boundary | Current maturity |
|---|---|---|---|
| `synergy_long_term_harness` | SHA-256 chunked, compressed append-only source archive; immutable record IDs; namespace checks; linked summaries; bounded byte-oriented context bundle; durable mission state, idempotency, lease fencing and local capability bridge | Evidence archive + mission/audit lifecycle; no network API and no shared typed federation contract | Main README-only; implementation on Draft stacked PR branches |
| `synergy_hierarchical_cognitive_memory_architecture` | Versioned semantic records; source snapshots; trust states; graph edges; FTS5 and optional vector retrieval; dynamic model-specific context/token budget planner; consolidation candidates | Semantic index/retrieval + context planning; optional API adapter warns against public exposure without auth/TLS/rate limits | Main README-only; implementation on Draft PR #1 |

**Overlap:** both define a SQLite-backed `MemoryStore`, namespaces, hashes/provenance, retrieval and bounded context assembly. **Not duplicates:** Long-Term Harness additionally owns mission idempotency/leases/verification and exact source chunk restoration; Hierarchical Memory additionally owns versioned knowledge records, graph/vector retrieval, trust/consolidation and model-profile token budgeting. Their main product files are not interchangeable.

**Decision:** KEEP both as separate candidate components; DEVELOP one shared typed memory boundary and an explicit layered integration. Preferred direction: immutable source archive and mission evidence remain the durable source layer; hierarchical memory becomes the semantic index/retrieval/context-planning layer over source references. Do not merge repositories or duplicate storage authority. Both remain uncontracted and no runtime edge is claimed until schema, namespace/source identity, auth, adapters and E2E evidence exist.

## Central registry validator and identifier reconciliation

A live consistency check found and corrected two independent validator/registry defects:

1. The owner inventory contains 92 repositories while the curated interface registry contains 76 components. The 76-row registry is an intentional subset, but the old validator required exact set equality. It now checks unique rows, declared count, and that every interface row belongs to the 92-repository owner inventory. The interface generator now uses the current interface registry as an explicit scope allowlist, so adding an owner repository does not silently turn it into a federation component.
2. Three interface/graph/contract references used pre-rename repository names. These have been reconciled to the canonical GitHub names: `Shtenco/synergy_binary_quantum_theory`, `Shtenco/synergy_epstein_network`, and `Shtenco/shtenco_multi_threaded_trading_robot_with_machine_learning_python`. Contract evidence paths retain their actual internal paths.
3. The old validator checked only `CONTRACT_FLOW` edges when requiring every cross-repository contract to appear in the dependency graph. The graph also represents typed contracts as `RUNTIME_CONTRACT`; after correction, all contract-bearing graph edges are considered. The live graph contains 38 unique cross-repository contract IDs across `CONTRACT_FLOW` and `RUNTIME_CONTRACT`; the one intra-repository contract (`execution-plan/v1`) correctly does not require a cross-repository edge.

Post-edit static reconciliation: 92 owner repos; 77 unique interface rows; all 76 are a subset of owner inventory; zero unknown graph endpoints; zero unknown contract producer/consumer names; all 38 cross-repository contracts have graph representation; 42 authorities; 39 contract records match 39 integration-gap records; adapter edge count remains 22. A direct static cross-check of the validator's current invariants returned zero errors. These are static registry checks, **not** a successful Actions run. The latest federation gate runs were still queued when inspected, and earlier failed runs had `runner_id=0` with no steps.





### Authority registry completion

The contract registry referenced 22 authority names absent from `AUTHORITY_REGISTRY.json`. I added all 22 with canonical owner, bounded `facts` and explicit `forbidden` claims derived from each contract's domain and payload schema. The authority registry now contains **42 authorities**. A static reconciliation against the live registries found:

- all 42 authority owners exist in the 92-repository owner inventory;
- every one of the 39 contract records resolves to a known authority;
- every contract authority owner matches that contract's producer;
- all producer and consumer names resolve to canonical owner repositories.

This preserves the policy that a producer may assert only its bounded domain facts; market signals, research, simulations, benchmark results and source-integrity evidence do not gain payment, accounting, capital, risk or execution authority. The validator now also enforces authority-owner/producer identity and cross-checks adapter, E2E, gap, uncontracted-component and risk totals against the dependency graph and integration-gap registry.

### Central validation runs after registry corrections

The latest exact-head validation runs are not yet executing:

- [Federation Maturity Gate run 44643358335](https://github.com/Shtenco/synergy_system/actions/runs/44643358335): queued; job `maturity-gate` has no runner ID and no steps.
- [Typed Contracts validation run 44643347370](https://github.com/Shtenco/synergy_system/actions/runs/44643347370): queued; job `contracts` has no runner ID and no steps.
- The preceding completed Federation validation run 44638380402 and Typed Contracts run 44635463730 both failed with `runner_id=0` and empty step arrays.

**Status:** central static registry reconciliation is internally consistent, but the code/registry fixes remain **BLOCKED_INFRA / CI-PENDING** until GitHub Actions assigns runners and the actual validators execute. Do not treat a queued job as green.

## CI / missed-test evidence

### `synergy_long_term_harness`, PR #1 exact head `bdc26413d886fb026bdc22c3a6f76dc2df873a1c`

- Workflow run: [44395090855](https://github.com/Shtenco/synergy_long_term_harness/actions/runs/44395090855)
- Four Python matrix jobs (3.10–3.13) concluded failure within roughly 3–4 seconds.
- All jobs report `runner_id=0`, empty `steps`, and no runner name.
- The workflow definition includes checkout, Python setup, compileall, unittest discovery and CLI smoke, but none of these steps appears in the failed jobs.
- The run logs endpoint returned an empty body in this inspection.

**Finding:** no test assertion or compile step is evidenced as having run. Classify the PR's CI as `BLOCKED — runner/job initialization failure suspected; root cause unavailable from exposed logs`, not as a failing test suite.

### `synergy_ai_language`, PR #35 exact head `f0d724f6cc2a84afa09049dc889bcd3eb753b5eb`

- Workflow run: [44451534644](https://github.com/Shtenco/synergy_ai_language/actions/runs/44451534644)
- Four Python matrix jobs (3.10–3.13) concluded failure in approximately two seconds.
- All jobs report `runner_id=0`, empty `steps`, and no runner name.
- The workflow definition includes checkout, setup Python, dependency installation, Ruff and pytest, but no job step was recorded.
- The run logs endpoint returned no readable log content in this inspection.

**Finding:** no lint or pytest execution is evidenced. Classify the PR's CI as `BLOCKED — runner/job initialization failure suspected; root cause unavailable from exposed logs`.

### Missed tests and evidence gaps

The absence of recorded steps means the intended tests were skipped before execution; it does not mean tests passed or failed. For the two PRs above, missing evidence includes checkout, dependency installation, compile/lint, unit tests and CLI/API smoke. The next validation must rerun the exact head SHAs after the runner issue is resolved, then inspect step-level output and test reports. Do not mark either PR MERGE-READY on the current evidence.



### Seven-product main-branch CI pass

The latest inspected workflow runs for the seven repositories' current `main` SHAs show **zero green runs in this sample**:

| Repository | Exact main SHA | Run | Observed job result | Evidence |
|---|---|---:|---|---|
| `synergy_market_maker` | `3edcea187c45866d55a65b74dc707b7b1009a69b` | [42536892178](https://github.com/Shtenco/synergy_market_maker/actions/runs/42536892178) | BLOCKED_INFRA | 1 job, failure in ~3s, runner_id=0, no steps |
| `synergy_adaptive_engine` | `c4af6194eedfbf9b9c0824822abe42306ba9f6b8` | [40047566286](https://github.com/Shtenco/synergy_adaptive_engine/actions/runs/40047566286) | BLOCKED_TEST_FAILURE | runner allocated; install succeeded; `pytest -q` failed |
| `synergy_riskguard` | `bc3ef1810c5d77f54b8a9ecf2f1b8adc35231f2b` | [40047487688](https://github.com/Shtenco/synergy_riskguard/actions/runs/40047487688) | BLOCKED_TEST_FAILURE | runner allocated; install succeeded; `pytest -q` failed |
| `synergy_trademux` | `fe584afeba1410f40640672f277be4ab16e76b8c` | [40054795636](https://github.com/Shtenco/synergy_trademux/actions/runs/40054795636) | BLOCKED_TEST_FAILURE | runner allocated; install succeeded; `pytest -q` failed |
| `synergy_relative_value` | `0f37ef55ac989933acd63a0954b5cf521eec4449` | [40047520007](https://github.com/Shtenco/synergy_relative_value/actions/runs/40047520007) | BLOCKED_TEST_FAILURE | runner allocated; install succeeded; `pytest -q` failed |
| `synergy_midas_institutional` | `75f646380cd0a1478e5093216615b1af8ded1fbf` | [40047508720](https://github.com/Shtenco/synergy_midas_institutional/actions/runs/40047508720) | BLOCKED_TEST_FAILURE | runner allocated; install succeeded; `pytest -q` failed |
| `synergy_marketvision` | `1baf9fa65c9974bb241f3a4fb2a352424bfe9bcc` | [40054785764](https://github.com/Shtenco/synergy_marketvision/actions/runs/40054785764) | BLOCKED_TEST_FAILURE | runner allocated; install succeeded; `pytest -q` failed |

For the six test-failure rows, checkout, Python setup and dependency installation succeeded; the failed step is explicitly `pytest -q`. The run log archive endpoints returned empty bodies in this inspection, so the exact failing test names, tracebacks and assertions are not yet known. Do not label a specific test as the cause without its log. For Market Maker, no step ran, so no pytest conclusion can be drawn.

**Impact:** all seven product domains remain KEEP as architectural components, but their current main-branch validation state is BLOCKED. Their adapter declarations and contract-registry entries are not a substitute for green tests or E2E evidence. No product is MERGE-READY on this evidence.



### Other priority PR CI states

The broader priority-PR evidence register also records:

- `synergy_long_term_harness` PRs #1–#4: failed workflows; all observed Python matrix jobs have empty step lists, so no compile/unit/CLI test execution is evidenced.
- `synergy_agi_autopilot` PRs #12, #13, #14, #18, #21 and #24: failures across desktop-renderer, Python sidecars, browser bridge and Rust platform jobs; the job-step endpoint returned empty step lists, so the test/build assertions are not evidenced as run.
- `synergy_hierarchical_cognitive_memory_architecture` PR #1: cancelled before steps; no test result.
- `synergy_motherboard_xpu_xml` PR #4: workflows were queued at inspection; no conclusion.
- `synergy_system` PR #54: no workflow run was visible for the exact inspected head.

The complete per-PR metadata and exact-head workflow records remain in [PR_BRANCH_DEPENDENCY_AUDIT_2026-11-20.json](../registry/PR_BRANCH_DEPENDENCY_AUDIT_2026-11-20.json). These states are not merge evidence; no PR in the inspected priority set is MERGE-READY.

## Status register

| Scope | Status | Rationale |
|---|---|---|
| Seven product repositories | KEEP / CI BLOCKED | Distinct product contracts and domain authorities; preserve boundaries, but current main CI is red or never started |
| Shared enterprise/runtime scaffold | DEVELOP | Confirmed repeated code; extract/version common foundation with migration tests |
| Long Term Harness PR #1 CI | BLOCKED_INFRA | All jobs failed before first recorded step; no test result |
| AI Language PR #35 CI | BLOCKED_INFRA | All jobs failed before first recorded step; no test result |
| MERGE-READY | None in this audit | No exact-head green CI plus complete review/evidence closure |
| ARCHIVE-CANDIDATE | None in this audit | Duplication is not sufficient evidence to archive a domain product |

## Limitations and next pass

- This focused pass covers seven trading repositories, not every source file in all 92 repositories.
- Git tree SHA equality proves exact blob identity for the compared files, not runtime equivalence of the whole products.
- The current CI connector surface exposed job metadata and an empty logs response; it did not expose readable runner logs or test annotations for these failed jobs.
- Continue with the remaining repository families (apps/web surfaces, AI agents/memory, blockchain/economic systems, compression/compute and science) using the same tree/SHA and contract/interface comparison method.


## Follow-up branch evidence — seven product repositories

Fourteen live main-vs-branch comparisons were added to the central ancestry ledger:

| Product | `enterprise/v2.0.0` | `production/v3.0.0` |
|---|---|---|
| RiskGuard | behind 11, ahead 0 | diverged, ahead 1 / behind 11 |
| TradeMux | behind 14, ahead 0 | diverged, ahead 1 / behind 14 |
| Market Maker | behind 13, ahead 0 | diverged, ahead 1 / behind 13 |
| Adaptive Engine | behind 10, ahead 0 | diverged, ahead 1 / behind 10 |
| MarketVision | behind 13, ahead 0 | diverged, ahead 1 / behind 13 |
| Relative Value | behind 12, ahead 0 | diverged, ahead 1 / behind 12 |
| MIDAS Institutional | behind 13, ahead 0 | diverged, ahead 2 / behind 11 |

The `production/v3.0.0` unique commits inspected in the compare response are design documents, not product implementation changes. The design documents identify real production-hardening gaps: caller-controlled risk limits/kill switch (RiskGuard), ambiguous POST retry and missing persistent OMS state (TradeMux), caller-supplied inventory/market data and no quote lifecycle (Market Maker), in-memory adaptive allocation state (Adaptive Engine), missing immutable feature artifacts/lineage (MarketVision), and missing model identity/freshness/OOS lifecycle (Relative Value). These branches remain `DEVELOP`, not merge-ready.

The `enterprise/v2.0.0` refs are behind-only and are marked `ARCHIVE-CANDIDATE` for review only. This does not authorize deletion: tags, releases, deployments and external references must be checked first. No merge-ready branch was identified.


## Main-branch CI root-cause pass — 2026-11-20

Seven latest inspected main-branch CI runs were examined at job and log level. Six executed pytest; one Market Maker job never acquired a runner.

| Repository | Run | pytest result | Root cause evidence |
|---|---:|---:|---|
| Adaptive Engine | [40047566286](https://github.com/Shtenco/synergy_adaptive_engine/actions/runs/40047566286) | 1 failed, 20 passed | FastAPI `_IncludedRouter` has no `.path`; route test inspects framework internals |
| RiskGuard | [40047487688](https://github.com/Shtenco/synergy_riskguard/actions/runs/40047487688) | 1 failed, 23 passed | Same fragile route test |
| TradeMux | [40054795636](https://github.com/Shtenco/synergy_trademux/actions/runs/40054795636) | 3 failed, 20 passed | Same route test; missing README `Version: 2.0.0`; `unfilled_notional` integral zero serialized as `0` rather than canonical `0.0` |
| Relative Value | [40047520007](https://github.com/Shtenco/synergy_relative_value/actions/runs/40047520007) | 2 failed, 19 passed | Same route test; missing README version marker |
| MIDAS Institutional | [40047508720](https://github.com/Shtenco/synergy_midas_institutional/actions/runs/40047508720) | 2 failed, 19 passed | Same route test; missing README version marker |
| MarketVision | [40054785764](https://github.com/Shtenco/synergy_marketvision/actions/runs/40054785764) | 2 failed, 18 passed | Same route test; missing README version marker |
| Market Maker | [42536892178](https://github.com/Shtenco/synergy_market_maker/actions/runs/42536892178) | Not executed | `runner_id=0`, empty steps; log download returned 404 BlobNotFound |

The common route-test defect is in `tests/test_enterprise_product.py`: it iterated over `app.routes` and read each `.path`. This relies on FastAPI's internal route object shape. The test was updated in all six repositories to inspect `app.openapi()["paths"]`, which checks the public API contract.

Release metadata markers were restored in the four affected README files (TradeMux, Relative Value, MIDAS Institutional, MarketVision). TradeMux's contract serializer now emits finite decimal strings in a canonical fixed-point form, including `0.0` for integral zero, and rejects non-finite monetary values.

### Remediation commits and revalidation

| Repository | Source/test/doc commit | New CI run |
|---|---|---|
| Adaptive Engine | `f0622aa6d60be3c47d2ac752b9ef686e6dac6c5b` | [44670168704](https://github.com/Shtenco/synergy_adaptive_engine/actions/runs/44670168704) |
| RiskGuard | `e5ba5eab09e42ac25c695740bdc464ef3617c33c` | [44670174126](https://github.com/Shtenco/synergy_riskguard/actions/runs/44670174126) |
| TradeMux | `0aafb097d3d442a4a5f0fc735e52bfa2c3071b8d` | [44670248392](https://github.com/Shtenco/synergy_trademux/actions/runs/44670248392) |
| Relative Value | `c9916f809ca60493b9c66a434e64ca8d8cb3d483` | [44670185726](https://github.com/Shtenco/synergy_relative_value/actions/runs/44670185726) |
| MIDAS Institutional | `a1c57d0466daf0e5e23c4ab4640d6a630d43ec67` | [44670191861](https://github.com/Shtenco/synergy_midas_institutional/actions/runs/44670191861) |
| MarketVision | `d7c2d66dd4ab7015230ad08139c6589740933e0b` | [44670201147](https://github.com/Shtenco/synergy_marketvision/actions/runs/44670201147) |

All six new runs were queued at the last status read; no success is claimed yet. Market Maker's failed job was explicitly re-run (attempt 2) and was queued at the last status read. The original test result remains unknown until that rerun obtains a runner and publishes steps/logs.

**Current classification:** all seven product repositories remain `DEVELOP` until the reruns are green. No product is `MERGE-READY`.


## Additional branch ancestry pass — Midas AI, AI Coder and Science Agent

Eight more exact `main...branch` comparisons were recorded in the central branch ledger:

| Repository / branch | Ahead | Behind | Decision |
|---|---:|---:|---|
| `synergy_midas_ai/feat/historical-strategy-evidence-registry-v1-20260821` | 29 | 63 | DEVELOP |
| `synergy_midas_ai/feat/independent-risk-decision-v1-20260821` | 39 | 63 | DEVELOP |
| `synergy_ai_coder/feat/autonomous-engineering-foundation-20261114` | 10 | 0 | DEVELOP |
| `synergy_ai_coder/feat/change-set-review-protocol-20260818` | 10 | 10 | DEVELOP |
| `synergy_ai_coder/feat/recursive-context-archive-integration-20261118` | 177 | 0 | DEVELOP |
| `synergy_nexus_science_agent/feat/science-service-protocol-v4-20260821` | 22 | 17 | DEVELOP |
| `synergy_nexus_science_agent/feat/search-evidence-graph-core-v1-20260821` | 8 | 17 | DEVELOP |
| `synergy_nexus_science_agent/feat/source-quality-identity-v3-20260821` | 16 | 17 | DEVELOP |

AI Coder's recursive context archive branch is 177 commits ahead and contains the archive codecs, byte-oriented context archive, semantic memory, scale benchmarks and integration tests; it is substantial, not a scratch branch. It still needs exact-head CI and a dependency/contract review before merge consideration. The two Midas branches share a large common V10 baseline and introduce historical-strategy registry and independent-risk-decision work; because they diverge and overlap, inspect their dependency/stack relationship rather than treating them as independent merge candidates. Science Agent's three branches share a common science core baseline but add service protocol, evidence graph and source-quality identity layers; their shared base and overlapping workflow additions require stack-aware integration.

The ancestry ledger now contains **127 / 1,202** non-main comparisons; **1,075 remain pending**. Counts: ahead 7, behind 17, diverged 103. No branch in this batch is merge-ready.


## Feature-branch Actions retry eligibility

The eight inspected feature-branch PR runs all failed/cancelled before a runner step (`runner_id=0`, empty steps). I attempted reruns where GitHub still permitted them:

- AI Coder run `43561808615` (autonomous engineering foundation): rerun accepted, attempt 2 queued.
- AI Coder run `44452576244` (recursive context archive integration): rerun accepted, attempt 2 queued.
- Midas AI runs `32453096236` and `32470135785`, AI Coder change-set run `32176942797`, and Science Agent runs `32506472197`, `32453305218`, `32470329120`: GitHub rejected rerun because each run was created over one month ago.

At the last status read, both accepted AI Coder reruns remained queued with no runner ID or steps. No new test execution is yet proven. The old-run retention/retry restriction is recorded as an evidence limitation, not a source-code failure.


### CI revalidation outcome — runner allocation remains the blocker

The new main-branch runs were polled after the fixes. Adaptive Engine (`44670168704`), RiskGuard (`44670174126`), Relative Value (`44670215047`) and MarketVision (`44670223496`) completed as failure with `runner_id=0` and empty steps. TradeMux (`44670775412`) and MIDAS Institutional (`44670219074`) were still queued at the last read; their job payloads had no executed steps. Market Maker's retry attempt 2 (`42536892178`) failed again with `runner_id=0`, empty steps. AI Coder's two accepted retry attempts (`43561808615`, `44452576244`) also failed with `runner_id=0`, empty steps.

This means the source/test fixes are committed but cannot yet be validated by Actions. The new CI failures are not test regressions: there are no test-step results. Do not revert the fixes based on these infrastructure-only run outcomes. Re-run exact HEADs when GitHub provides an assigned runner; only then assess whether the route assertions, release metadata and TradeMux decimal tests pass.


## Central federation workflow evidence

The central repository's latest federation/contract validation runs were also inspected:

- [Federation Maturity Gate 44669941281](https://github.com/Shtenco/synergy_system/actions/runs/44669941281): failed with `runner_id=0`, no steps.
- [Typed Contracts 44644066903](https://github.com/Shtenco/synergy_system/actions/runs/44644066903): failed with `runner_id=0`, no steps.
- [Federation Maturity Gate 44644066897](https://github.com/Shtenco/synergy_system/actions/runs/44644066897): failed with `runner_id=0`, no steps.
- Newer runs [44670752433](https://github.com/Shtenco/synergy_system/actions/runs/44670752433) and [44670862728](https://github.com/Shtenco/synergy_system/actions/runs/44670862728) were queued at the last check.

The central validators therefore have not yet supplied evidence that the latest registry/doc updates pass or fail their assertions. Their current state is `BLOCKED — runner not assigned / no step execution evidence`; do not report the typed contract validator as failing schema assertions.


## Finance, blockchain and Meta OS branch relationships

Ten additional branch comparisons were added to the central ancestry ledger. All ten are diverged from their current `main`; the key branch-to-branch comparisons reveal:

- Financial OS `feat/distribution-available-capacity-v4-refund-restored-20260828` is **219 commits ahead** of `feat/accounting-close-merkle-v1-20260818` with no commits behind: it is a direct descendant/stack continuation, not an independent feature line.
- Financial OS `feat/external-profit-import-v1-20260905` is **6 commits ahead** of the distribution-capacity V4 branch with no commits behind. Treat the three as an ordered stack: accounting-close Merkle → distribution capacity/refund restoration → external-profit import.
- Meta OS `feat/autopilot-v5-ai-node-production-bootstrap-v5-rc5-20260824` and `feat/durable-supervisor-state-v3-20260821` are diverged relative to each other (121 ahead / 14 behind); they are not a clean linear stack and require conflict-aware integration.
- Blockchain persistent-restart evidence and trust-state proof branches are each extremely far behind current main (932 commits) while retaining 37 and 18 unique commits respectively. Preserve the evidence work, but do not treat it as merge-ready without rebase/port strategy and current tests.
- AI Language semantic-memory bridge (152 ahead / 63 behind) and accounting-close requirements branch (20 ahead / 56 behind) are divergent; the semantic-memory schema candidate is not yet in canonical main or central contract registry.

All ten branches are `DEVELOP`; none is `MERGE-READY`. The central branch ledger now contains **137 / 1,202** non-main comparisons, with **1,065 pending** (ahead 7 / behind 17 / diverged 113).


### Additional two product repositories in the exact duplicate intersection

A second tree comparison added `synergy_ai_investment_committee` and `synergy_quantlab`. Across all nine repositories, **63 normalized paths exist in every tree and 29 have identical blob SHA in all nine**. The added products retain distinct product contracts:

- Investment Committee: `synergy.trading.investment-thesis/v1`, authority `investment_committee`.
- QuantLab: `synergy.trading.validation-decision/v1`, authority `trading_validation`.

The pairwise matrix above remains the detailed 21-pair matrix for the original seven repositories; the nine-way intersection is an additional exact common-core proof. All nine products remain separate and `KEEP`.
