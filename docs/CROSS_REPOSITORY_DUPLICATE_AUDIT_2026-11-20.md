# Cross-repository functional duplication and CI evidence audit — 2026-11-20

## Scope and method

This is a focused, source-backed pass over seven active trading/runtime repositories. It is not yet a claim that all 92 repositories have been compared file-by-file. Git Trees were read from each repository's `main` at the SHAs listed below. Paths under `src/<package-name>/` were normalized to `src/PACKAGE/`; Git blob SHA equality was used as an exact-content test. Similar path names alone were not counted as duplicates.

## Executive finding

Seven separately named trading products share a highly repeated enterprise/runtime scaffold. Across the 21 repository pairs:

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



### Seven-way common-code intersection

A second intersection check across all seven repositories confirms **63 normalized paths are present in every repository and 29 of those paths have the same blob SHA in all seven**. The 29-way identical set is:

- `.env.enterprise.example`, `.github/workflows/ci.yml`, `.gitignore`, `CHANGELOG.md`;
- `deploy/clickhouse/001_audit.sql`, `deploy/postgres/001_audit.sql`;
- `docs/AUDIT_DATA_MODEL.md`, `docs/ENTERPRISE_DEPLOYMENT.md`, `docs/LOAD_TESTS.md`, `docs/PRODUCT_STATUS.md`, `docs/RBAC.md`, `docs/SECURITY.md`;
- `loadtests/benchmark.py`, `loadtests/k6_smoke.js`;
- `src/PACKAGE/__init__.py` and the common enterprise package initializers, Bybit/CCXT/MT5 adapters, audit, auth, metrics, models, resilience and service modules;
- `tests/test_customer_demo.py`, `tests/test_enterprise_deployment.py`.

The seven `core.py`, `api.py` and `synergy_contracts.py` files each have **seven distinct blob SHAs**. This independently supports keeping the seven product domains separate while treating the enterprise scaffold as shared code to extract.

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

## Recommended architecture change

1. Keep all seven product repositories and their domain-specific cores.
2. Develop one versioned shared enterprise foundation package for reusable auth, audit, metrics, adapter interfaces, resilience, service plumbing and common deployment/test helpers.
3. Keep each product's `core.py`, product API surface and SYNERGY contract owned by its domain repository.
4. Give the shared package a stable semantic version and compatibility policy; migrate one product at a time.
5. Add contract tests proving each product's adapter implements the shared interface, and integration tests at the actual producer/consumer boundaries.
6. Do not create a new shared repository until ownership, dependency direction, release policy and migration tests are agreed. Avoid a hurried bulk extraction.

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
