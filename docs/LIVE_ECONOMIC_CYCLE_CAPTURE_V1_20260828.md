# SYNERGY Live External Value → Next Capacity Capture Candidate v1

This layer exists to close the highest-value remaining Economic OS blocker without allowing a JSON document to self-assert that a live economic cycle happened.

It is a **capture candidate contract**, not live execution evidence by itself.

## Bound protocol roots

EconomicCycle v1:

`83f9c3ee0c168ca50212ebaa1e64c58c08eb87fd040a8b5f214ee4987242f3f1`

Economic OS RC4:

`51566c3c87f21b1a22ddef9bb6aea6abd9170042790f37ac3ff559bf7ad89c60`

## Exact event-instance chain

One candidate must contain one `run_id` and exactly these 12 ordered artifacts from the same causal run:

1. external value settlement evidence;
2. revenue recognition;
3. canonical ledger / AccountingClose / EconomicCycleTrace v6;
4. fee-aware distribution BudgetState v2;
5. AvailableCapacity v3;
6. human committee or multisig ExecutionTicket v3;
7. MetaPay DistributionUtilization v3;
8. Financial OS fee accounting v3;
9. later MetaPay settlement reversal v2;
10. Financial OS reversal accounting v2;
11. BudgetState v3 entitlement restoration;
12. AvailableCapacity v4 for the next cycle.

Every phase binds its exact artifact digest and observation time.

## External-evidence boundary

Phases 1, 7 and 9 additionally require a provider claim containing:

- provider identity;
- provider reference;
- provider evidence digest;
- environment exactly `LIVE_EXTERNAL`;
- status exactly `PENDING_EXTERNAL_VERIFICATION`.

Names/references containing `MOCK`, `SYNTH`, `SIMULAT`, `LOCAL_ONLY` or `TEST_FIXTURE` fail closed.

This is deliberately only an admissibility gate. A provider reference written into JSON is **not proof that the provider actually emitted it**. Therefore this generation refuses any self-asserted `VERIFIED` status.

## Economic conditions

A structurally complete candidate must show:

- `canonical_hard_nav_after > canonical_hard_nav_before`;
- `realized_external_pnl_after > realized_external_pnl_before`;
- negative starting realized P&L is allowed;
- terminal `AvailableCapacity v4` status is `CAPACITY_AVAILABLE` with strictly positive capacity;
- internal mint/revaluation contribution to recognized profit is exactly zero;
- distribution approval is human committee or multisig only;
- AI authority is NONE;
- settlement reversal leaves the original authorization consumed.

## Status boundary

The only accepted candidate status is:

`STRUCTURALLY_COMPLETE_PENDING_EXTERNAL_VERIFICATION`

with:

`external_verification_status = PENDING`

and:

`live_execution_claim = false`.

A fresh hash cannot promote the same object to `LIVE_EXTERNAL_VALUE_TO_NEXT_CAPACITY_VERIFIED`.

A later generation must independently inspect the actual external provider evidence and exact canonical artifacts before it may create a separate finalized live-cycle evidence object.

## Test fixtures

The test suite builds synthetic in-memory objects to exercise structural verification. Those objects are deliberately **not written to the repository as live evidence** and do not remove the current blocker:

`ONE_LIVE_EXTERNAL_VALUE_TO_NEXT_CAPACITY_EXECUTION_NOT_CAPTURED`.
