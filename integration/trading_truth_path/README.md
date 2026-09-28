# Trading Truth Path — Cross-Repository Integration Harness

This harness is the promotion gate from `ADAPTER_IMPLEMENTED` to `E2E_TESTED` for the first SYNERGY vertical:

```text
MIDAS
→ QuantLab
→ RiskGuard
→ TradeMux
→ Pay System
→ Financial OS
→ AI Blockchain
```

## What it proves

It runs the contract-specific tests in every independently owned repository and the blockchain domain-commitment test.

It verifies fail-closed boundaries such as:

- rejected validation cannot become an order intent;
- RiskGuard REJECT/KILL_SWITCH cannot route;
- TradeMux fills are only expected internal settlement evidence;
- unreconciled settlement cannot become accounting recognition;
- Financial OS entries must balance;
- blockchain commits authoritative bytes without reinterpreting accounting.

## What it does NOT prove

- live broker/exchange execution;
- production settlement;
- future trading profitability;
- production deployment.

## Run

Place the seven repositories as sibling directories and set:

```bash
export SYNERGY_REPOS_ROOT=/path/to/repos
python synergy_system/integration/trading_truth_path/run.py
```

Set `SYNERGY_VERIFY_LOCK=1` to require exactly the commits in `integration_lock_v1.json`.

The integration lock is provenance, not an automatic update mechanism.
