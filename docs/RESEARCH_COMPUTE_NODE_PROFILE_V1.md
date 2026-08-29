# RESEARCH_COMPUTE_NODE profile v1

`synergy.node-profile/v1` is the architecture-level composition contract for a non-financial SYNERGY research node.

## Purpose

The first cross-root node intentionally combines only three capabilities:

- `P2P_RELAY` — SynergyNet transport;
- `CONTENT_CACHE` — SynergyNet content-addressed cache;
- `NEXUS_COMPUTE` — canonical AGI NEXUS compute.

The profile requires exactly these services:

- `synergynet` from `Shtenco/synergynet`;
- `content-cache` from `Shtenco/synergynet`;
- `nexus` from `Shtenco/agi_nexus`.

It explicitly forbids service kinds `METAPAY`, `FINANCIAL_OS`, `BLOCKCHAIN`, and `AUTOPILOT`.

## Authority boundary

The profile is architecture metadata only. It always carries:

- `financial_authority = NONE`;
- `payment_authority = NONE`;
- `accounting_authority = NONE`;
- `execution_authority = NONE`.

A valid node-profile digest proves exact architecture bytes. It does not sign a node manifest, execute a service, move money, validate blockchain consensus, or grant any financial privilege.

## Producer and consumer

- producer: `Shtenco/synergy_system`;
- consumer: `Shtenco/synergy_meta_os`.

`synergy_meta_os` must independently verify a signed node manifest against these profile bytes. A valid manifest signature is necessary for node identity but is not sufficient for architecture-profile conformance.

## Canonical fixture

The v1 research profile is stored at `fixtures/node_profiles/research_compute_node_v1.json` and has profile digest:

`406740705e853fa51ad4eacf7a01925fbe4b5cec491be35ea12ba777d217d714`

## Security invariant

A correctly signed manifest that adds `METAPAY_GATEWAY`, `FINANCIAL_SERVICE`, `BLOCKCHAIN_VALIDATOR`, or any forbidden service is still invalid for `RESEARCH_COMPUTE_NODE`.

Identity, capability possession, architecture authorization, and financial authority remain separate concepts.
