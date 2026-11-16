# Research Compute Node — canonical durable-artifact Readiness v6

Readiness v6 is an additive correction over v5. No v1-v5 evidence is edited or deleted.

## Why v6 exists

After durable binary locations were introduced, an independent canonical re-hash showed that both first-generation `synergy.artifact-location-evidence/v1` envelopes contained self-digest values that did not equal the canonical hash of their own published JSON. The locator semantics themselves (artifact SHA-256/size, connected Drive file IDs and pre-upload checks) were preserved, but the evidence envelopes could not be canonical roots.

The mismatch is preserved as negative evidence:

`f17fdeab2dceb1aca3d939b57a6d5374eba6988c5f7b991ad80d3e9523d4e107`

Corrected domain-owned envelopes are:

- NEXUS LocationEvidence v2: `341989039238b9735018bad71c2ac1f0114ae15b4736faa524b5f7a643c27f47`
- SynergyNet LocationEvidence v2: `c4102a8e668b79fc961a5f1767154154f4a600d320442770d74c7a006a5cee08`

Each v2 envelope binds both its canonical self-digest and the fetch-time rule `FETCH_BY_PROVIDER_FILE_ID_THEN_VERIFY_SHA256_AND_SIZE_BEFORE_EXECUTION`. Evidence-envelope identity therefore cannot substitute for artifact-byte verification, and artifact presence cannot substitute for evidence integrity.

## Canonical roots

- ArtifactSet v4: `d479b71a0756288b5d8d6d7d7433881cbd448a63c22bc9f87f271df7f82479c2`
- BuildPlan v7: `46a4ee4c01fba5fb8c5e3cff51b4f6b5e7090347ef1ec1ab6763a606a31aaa2e`
- Readiness v6: `6714beff9f366ed19c6b000b9239afffcd797cfc9d3fc4319b70a8af53b9af1f`

The prior v5 chain is retained as superseded evidence because it depended on the rejected v1 location envelopes.

## Authority boundary

Readiness v6 is still only `NODE_ADMISSION_READY_NOT_RUNNING` with an empty build/readiness blocker set. It does not launch anything.

- `auto_start=false`
- `financial_authority=NONE`
- `payment_authority=NONE`
- `accounting_authority=NONE`
- `execution_authority=NONE`
- NEXUS `network_access=NONE`
- NEXUS `process_execution_authority=NONE`

Financial OS and MetaPay remain outside this authority domain. The next transition is Meta-OS admission/deployment planning; host binding, supervisor materialization and executed host evidence remain separate gates even after artifact locators are canonical.
