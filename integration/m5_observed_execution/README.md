# M5 — Observed Federation Execution

M5 is the promotion gate between implemented adapters and real end-to-end proof.

Current frozen coverage:

- M3: 22 runtime edges
- M4 Market Advisory: 5
- M4 Wave 2: 5
- M4 Wave 3: 5
- M4 Wave 4: 5
- M4 Wave 5: 2
- Total: **44 / 44 ADAPTER_IMPLEMENTED runtime edges**

## Non-negotiable rule

No runtime edge may be promoted to `E2E_TESTED` merely because code, schemas, harnesses or verifiers exist.

Promotion requires:

1. the exact pinned integration suite to execute;
2. an evidence JSON artifact to be physically produced;
3. that suite's verifier to pass;
4. the union of all suite scopes to match the registry's 44 implemented/tested/deployed runtime edges;
5. no duplicate or missing runtime edge;
6. the aggregate M5 verifier to pass.

## Current state

GitHub Actions is presently failing before the first workflow step. The observed failed jobs have no executed steps and no runner assignment. A re-run reproduced the same condition.

Therefore the honest maturity state remains:

```text
ADAPTER_IMPLEMENTED 44
E2E_TESTED          0
DEPLOYED            0
```

The files in this directory deliberately preserve that boundary. They make false promotion mechanically harder rather than hiding the infrastructure problem.
