# SYNERGY Federation V5 Operations

## Source of truth

Edit only:

- `config/repository_catalog_v5.json`
- federation-level contract schemas under `config/`

Do not hand-edit files under `generated/`.

## Generate

```bash
python scripts/generate_federation_v5.py
```

This derives:

- repository registry
- authority map
- capability registry
- SHTTPS trust-source projection
- exchange-object registry
- federation graph
- status matrix

Every generated JSON is bound to the same catalog digest.

## Verify

```bash
python -m unittest -v   tests.test_repository_catalog_v5   tests.test_federation_v5_policy   tests.test_capability_registry_v2   tests.test_exchange_objects_v1   tests.test_federation_v5_generation   tests.test_federation_v5_trust_projection   tests.test_federation_v5_regression

python scripts/check_federation_v5.py
python scripts/validate_federation_trust_source.py generated/federation_trust_source_v5.json
```

## Live GitHub inventory

Private repositories cannot be inferred safely from an unauthenticated CI request. Export the authorized inventory into a JSON file and verify it explicitly:

```bash
python scripts/check_federation_v5.py --inventory-json /secure/path/github_inventory.json
```

The inventory may be either:

```json
{"repositories":["repo_a","repo_b"]}
```

or a list of objects containing `name`.

Any difference from the canonical catalog fails with `E_INVENTORY_DRIFT`.

## Authority rule

```text
Repository
  != Federation principal
  != trusted node
  != capability
  != authority
```

The runtime path is:

```text
Repository Registry
 -> Lifecycle
 -> Capability
 -> Authority
 -> Trust eligibility
 -> PQ identity
 -> SHTTPS authentication
 -> caller ACL
 -> capability validation
 -> canonical object
 -> evidence
```

## Current observed inventory

The design was approved when 58 repositories were visible. By 2026-09-18 the authorized GitHub inventory contained 59 after `synergy_agi_trader` appeared.

The new repository is intentionally classified as R&D with no trust, financial, accounting, payment, settlement or execution authority. This demonstrates why repository count is derived rather than hard-coded.

## Merge boundary

Generation or validation never implies merge approval. PR #49 must remain unmerged until a human explicitly authorizes merge.
