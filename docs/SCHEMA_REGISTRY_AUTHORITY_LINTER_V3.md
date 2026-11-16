# Cross-Repo Schema Registry and Authority Linter v3

This generation adds two governance controls without making `synergy_system` an execution authority.

## Schema ownership registry

`config/cross_repo_schema_registry_v1.json` records the current producer and consumers of critical federation contracts. A consumer does not become producer authority by parsing a schema. Superseded generations are intended to remain registered rather than being silently removed.

Domain contracts such as current MIDAS, Meta-OS and Science Agent artifacts are marked `DOMAIN_INTERNAL` until an explicit cross-repository handoff is designed.

## Authority-transition linter

The linter examines **added lines** in code/config/schema paths for authority claims. It is deliberately conservative and narrow:

- accounting authority belongs only to `synergy_financial_os`;
- payment/settlement authority belongs only to `synergy_pay_system`;
- architecture authority belongs only to `synergy_system`;
- scientific-truth authority has no software owner and must remain NONE;
- generic non-NONE execution authority is restricted to explicitly execution-domain repositories and still requires human review.

Documentation/tests are excluded because examples may discuss forbidden authority. This also means the linter is not a security proof and cannot replace code review, schema validation or runtime capability enforcement.

## Deployment boundary

V3 is an offline deterministic engine/CLI. Organization-wide automatic enforcement requires a read-only/PR GitHub App or webhook installation that feeds exact changed-file patches into this engine. Until that integration exists, status is `DETERMINISTIC_PR_LINT_POLICY_NOT_SECURITY_PROOF`.

`synergy_system` remains architecture/governance metadata only and has `execution_authority=NONE`.
