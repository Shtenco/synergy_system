# Source-tree review of the 20 newly discovered repositories

**Date:** 2026-11-24  
**Scope:** repository root tree and selected source manifests; no claim that all tests were executed.

## Summary

The 20 repositories missing from the 2026-11-20 inventory are not all empty. The source-tree review found:

- `synergy_agent_long_term_memory` is placeholder-only: its root contains only a 32-byte README.
- `synergy_ai_browser-` has a Python package, examples, docs and tests; it is an evidence-first Playwright automation candidate.
- `tiimeweb_synergy_exactly_once_delivery` has experiments, results and tests.
- The 17 `timeweb_synergy_*` research repositories mostly share a common small experiment runner/scaffold while keeping separate article-specific experiment modules and result artifacts.
- `timeweb_synergy_retry_storm_lab` is a more independent source layout with `src/retrystorm`, scripts, tests and result data.

## The most important associative finding: one research series, not 17 unrelated platforms

Across the reviewed source manifests, several files recur with identical SHA-256 digests:

| Shared file | Repeated SHA-256 |
|---|---|
| `prototypes/__init__.py` | `7ea3e33621d03c4e3e2271d2e93e55721d45d99472f589fa698ec105fcddfdb6` |
| `prototypes/__main__.py` | `c63aff76bcd5a382a42c8d13eb3c2f5fb2c564b451bdfd20819631c3725055d6` |
| `prototypes/runner.py` | `3e1a59a8d2260be864749b4aa583961569fdcbee7b161f1025ae3725a841306f` |
| `prototypes/scenarios/__init__.py` | `60d32f11ef7875e4b24eedf3a631281803e0295a8206e39819cf2cae243632f8` |
| `requirements.txt` (in multiple repositories) | `12b84930f4edd3f3d1fde62f07d61110a07a88bdfb5acc5338f7fda8a61b8247` |

This is evidence of a shared harness lineage, not proof that all repositories are exact duplicates. Article-specific files, tests and results differ. Some repositories also share test modules across article groups.

### Recommended architecture

Do not merge the 17 experiments into one giant repository and do not copy the shared harness forever.

1. Keep each research topic as a separately citable experiment with its own question, data, results and limitations.
2. Extract the repeated runner, CLI, manifest validation and result-schema logic into a versioned shared HIAI research harness.
3. Let `synergy_nexus_science_agent` orchestrate discovery, experiment selection, provenance and falsification.
4. Let `synergy_ai_coder` verify requirement-to-evidence traces and artifact hashes.
5. Let `timeweb_synergy_benchmark_statistics` and `timeweb_synergy_ml_validation_lab` provide independent statistical/validation gates.
6. Require each experiment to pin the harness version and retain its own environment, dataset, seed, result and SHA-256 evidence.

This turns a collection of article experiments into a reusable research product: reproducibility runner + evidence registry + benchmark governance + scientific agent.

## New-repository findings

| Repository | Root/source evidence | Initial status boundary |
|---|---|---|
| `synergy_agent_long_term_memory` | README only | Placeholder; no code/tests |
| `synergy_ai_browser-` | `synergy_browser/`, `tests/`, `examples/`, `pyproject.toml` | Source/test tree present; bounded browser automation |
| `tiimeweb_synergy_exactly_once_delivery` | `experiments/`, `results/`, `tests/` | Experiment/test tree present |
| `timeweb_synergy_agent_long_term_memory` | Source manifest, prototypes, tests, results | Limited prototype; article 13 |
| `timeweb_synergy_ai_infrastructure_agent` | 9-file source manifest, prototypes, test path | Limited allowlist-oriented prototype |
| `timeweb_synergy_backtest_oos_lab` | 9-file source manifest, prototypes, tests | Article 10 OOS/backtest experiment |
| `timeweb_synergy_benchmark_statistics` | 12-file source manifest, tests, result JSON | Measured local uncertainty experiment |
| `timeweb_synergy_binary_neural_networks` | 16-file source manifest, tests, result JSON | Local binary-network experiment |
| `timeweb_synergy_codebase_intelligence` | 9-file source manifest, prototypes, tests | Article 04 codebase search experiment |
| `timeweb_synergy_cpu_gpu_cost_benchmark` | 9-file source manifest, prototypes, tests | Target-hardware cost experiment |
| `timeweb_synergy_cpu_language_model` | 14-file source manifest, evidence, tests, results | CPU toy-model experiment |
| `timeweb_synergy_fault_injection_lab` | 7-file source manifest, experiments, QA and results | Local fault-injection experiment |
| `timeweb_synergy_llm_memory_lab` | 11-file source manifest, evidence and tests | Synthetic memory/retrieval prototype |
| `timeweb_synergy_ml_validation_lab` | 19-file source manifest, tests and results | Dataset-specific leakage/overfitting experiments |
| `timeweb_synergy_multiagent_benchmark` | 9-file source manifest, prototypes and tests | Coordination-cost benchmark |
| `timeweb_synergy_python_cpp_performance` | 31-file source manifest, C++ kernels, tests and results | Local performance measurements |
| `timeweb_synergy_rag_quality_cost` | 9-file source manifest, prototypes and tests | RAG quality/cost experiment |
| `timeweb_synergy_retry_storm_lab` | `src/retrystorm/`, scripts, tests and results | Independent local HTTP resilience experiment |
| `timeweb_synergy_rnn_transformer_benchmark` | 12-file source manifest, tests and results | Equal-budget sequence-model experiment |
| `timeweb_synergy_service_recovery` | 9-file source manifest, prototypes and tests | Local service recovery experiment |

## Productization opportunities

### 1. HIAI Research Workbench

A unified interface to run, compare and reproduce experiments. Monetization: institutional license, hosted workspaces and reproducibility services.

### 2. Evidence and Benchmark Registry

A versioned catalogue of datasets, methods, model versions, seeds, result files, uncertainty intervals and limitations. Monetization: private benchmark registries and independent evaluation.

### 3. Resilience Engineering Toolkit

Combine Retry Storm, Fault Injection, Service Recovery and Exactly Once Delivery into an API reliability testing suite. Monetization: CI integration, enterprise SRE reports and recurring assurance.

### 4. Efficient AI Deployment Lab

Combine CPU language models, BNN, Python/C++ performance, CPU/GPU cost, model compression and Computing Topology. Monetization: model deployment optimization and measured cost-per-inference reduction.

### 5. Knowledge Systems Evaluation Suite

Combine LLM Memory Lab, Agent Long-Term Memory, RAG Quality/Cost, Hierarchical Cognitive Memory and NEXUS Science Agent. Monetization: enterprise memory/RAG evaluation and governance.

## What remains unproven

- No tests were executed as part of this root-tree pass.
- File manifests prove declared file hashes, not correctness of every experiment.
- Local measurements do not establish general hardware or model superiority.
- Synthetic retrieval does not establish production RAG quality.
- A research prototype is not a production service or a Timeweb-approved commercial product.
- The placeholder-only `synergy_agent_long_term_memory` should not be confused with the separate Timeweb memory experiment.

**Conclusion:** the strongest new association is to consolidate repeated research infrastructure—not research topics—into a reusable, evidence-governed HIAI workbench.
