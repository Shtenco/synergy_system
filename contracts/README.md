# SYNERGY Typed Contracts V1

This directory is the machine-readable boundary layer of the 75-repository SYNERGY federation.

## Canonical layers

- `schemas/` — language-neutral JSON Schema 2020-12 contracts.
- `python/` — Pydantic reference models and canonical payload hashing.
- `proto/` — Protobuf wire/RPC representation for the primary economic/trust path.

## Envelope invariant

Every event carries `contract_id`, `schema_version`, `event_id`, `trace_id`, producer/authority identity, canonical payload SHA-256, evidence references and parent event IDs.

## Versioning

Compatible additive evolution remains within V1. Breaking semantic or structural changes require a new contract major version (for example `.../v2`) and a migration adapter.

## Authority

A schema defines bytes; it does not grant authority. Authority ownership is defined in `registry/AUTHORITY_REGISTRY.json`.

## Integration maturity

`DOCUMENTED → CONTRACT_DEFINED → PRODUCER_IMPLEMENTED → CONSUMER_IMPLEMENTED → ADAPTER_IMPLEMENTED → E2E_TESTED → DEPLOYED`.
