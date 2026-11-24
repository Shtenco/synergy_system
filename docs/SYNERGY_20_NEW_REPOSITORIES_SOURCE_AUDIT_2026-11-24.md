# Source snapshot — 20 repositories added to the live SYNERGY inventory

**Observed:** 2026-11-24  
**Scope:** main-branch tree inventory, branch counts and selected source/CI inspection.  
**Status:** structural review only; not a full source/security/production audit.

## Portfolio snapshot

- 20 repositories checked; 19 public and 1 private.
- 19 have at least one source file; 1 is README-only.
- 19 have at least one CI workflow; the README-only stub has none.
- 18 repositories have one branch; the stub and private browser repository have two branches each.
- 18 repositories have at least one test module; the fault-injection lab has a QA validator outside the tests tree but no unit-test module; the README-only stub has no tests.
- Exact main tree SHAs, file counts, branch counts, workflow paths and test paths are recorded in `registry/SYNERGY_20_NEW_REPOSITORIES_SOURCE_SNAPSHOT_2026-11-24.json`.

These are structural counts. They do not certify test success, scientific validity, security or deployability.

## Findings requiring action

### P1 — Fault-injection QA validator is not self-contained

`timeweb_synergy_fault_injection_lab/qa/validate.py` reads `manuscripts_md/`, `html/`, `word/` and `results/16/` files that are absent from the complete public `main` tree. The script also imports `python-docx` and `bs4`, while `requirements.txt` declares only pytest. The checked-in `research-ci.yml` compiles Python and checks documentation but does not run this validator. The README says editorial materials live in a separate offline archive, so the validator must either be split into a public-artifact check and an optional private-archive check, or the required artifacts/dependencies must be provided under an explicit access policy.

### P1 — Exactly-once tests do not exercise the core invariant

`tiimeweb_synergy_exactly_once_delivery` contains a substantive SQLite experiment: transactional deduplication, concurrent duplicate deliveries, crash-before/after-commit probes and payload-conflict rejection. But its only unit-test module checks helper functions (`fingerprint` and `quantile`), and the inspected `research-ci.yml` does not run tests. The experiment itself correctly limits its claim to exactly-once effects inside one SQLite transaction, not transport delivery or external API side effects. Add CI tests for duplicate delivery, crash/restart, concurrent contention, payload conflict and invariant-preserving recovery.

### P1 — Long-term-memory naming/ownership ambiguity

`synergy_agent_long_term_memory` has one file on `main` (README only), two branches, no source/tests/CI. A separate `timeweb_synergy_agent_long_term_memory` repository has an executable SQLite cross-session persistence experiment, tests and CI. Its own source explicitly limits the claim: SQLite persistence, not LLM semantic memory or full agent long-term memory. Confirm whether the stub is a superseded concept, an independent product boundary or a duplicate; record the canonical owner and lineage before treating both as separate capabilities.

### P2 — Research CI commonly checks syntax, not behavior

The inspected `research-ci.yml` template in the LLM-memory, ML-validation, fault-injection and exactly-once repositories compiles Python modules and checks minimum documentation but does not execute their unit tests or experiment assertions. In contrast, `timeweb_synergy_retry_storm_lab` runs unittest on Python 3.10/3.12/3.13 and compileall; `timeweb_synergy_agent_long_term_memory` runs unittest, compileall and a SQLite smoke experiment. Promote this distinction into the portfolio's CI maturity labels; do not treat a green syntax-only workflow as behavioral validation.

## Positive evidence

- `timeweb_synergy_retry_storm_lab` has three test modules covering faults, integration and policies; CI executes them across three Python versions. Its README/experiment scope remains a localhost controlled lab, not a multi-region SLO proof.
- `timeweb_synergy_agent_long_term_memory` tests persistence across four SQLite connections and documents its limitations explicitly.
- `synergy_ai_browser-` has five test modules and separate tests/live-smoke workflows; exact-head workflow evidence and safety boundaries remain to be checked.
- Several other labs include focused test modules and research artifacts (group leakage, measured uncertainty, real sequence/text experiments, C++ benchmarks), but workflow execution and independent reproduction remain pending.

## Recommended next steps

1. Make fault-injection QA self-contained and add it to CI.
2. Add behavior-level exactly-once tests to CI, not just helper tests.
3. Resolve the two long-term-memory repository ownership/lineage question.
4. For each research lab, make CI run its test suite; separate syntax/documentation checks from behavioral checks.
5. Reproduce benchmark results from clean environments with pinned dependencies, seeds, raw artifacts and independent baselines.
6. Continue full source/security/dependency review; this snapshot does not inspect all code or Git history.

**Evidence rule:** repository count, source-file count, a test filename or a green syntax-only workflow is not a product-readiness metric.
