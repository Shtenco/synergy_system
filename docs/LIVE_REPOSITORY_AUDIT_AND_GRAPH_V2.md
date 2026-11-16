# Live repository audit & architecture graph v2

V2 adds observed repository metadata without changing `repository_federation_v1.yaml`.

## Static vs live facts

- `repository_federation_v1.yaml` is the architecture/governance declaration.
- `expected_repositories_v1.json` is the frozen inventory expected by the validator.
- `repository-live-audit/v1` is an observed snapshot of GitHub repository existence/default branch/privacy/archive state.

A live audit has `architecture_authority=NONE` and `execution_authority=NONE`. GitHub metadata cannot rewrite the architecture constitution automatically.

## Authentication

Because the federation contains private repositories, a truthful live audit requires a dedicated read-only GitHub App/PAT visible to every repository in scope. The current repository's ordinary `GITHUB_TOKEN` is not assumed to have organization-wide/private cross-repository access.

CLI:

```bash
SYNERGY_GITHUB_READ_TOKEN=... python tools/live_repository_audit.py
```

Without the credential the CLI returns `AUTH_REQUIRED`; it never reports a partial public-only inventory as complete.

## Architecture graph

`synergy.architecture-graph/v2` deterministically materializes nodes, typed dependency edges and strongly connected components from the existing federation manifest.

The current intentional bidirectional component is only:

`Shtenco/synergy_financial_os ↔ Shtenco/synergy_pay_system`

representing authorization in one direction and settlement/reconciliation evidence in the other.

The graph is presentation/governance evidence only and has no execution authority.
