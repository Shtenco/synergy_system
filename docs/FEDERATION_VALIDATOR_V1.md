# SYNERGY federation validator v1

The architecture root now has an executable check rather than relying only on prose review.

## Checks

- exact expected repository set: 37 repositories in v1;
- duplicate YAML keys rejected before semantic parsing;
- repository IDs unique;
- all exclusive-authority owners exist in the repository map;
- architecture root cannot gain execution authority;
- presentation/public/client/control-plane repositories cannot gain non-`NONE` authority fields;
- dependency endpoints must exist;
- self dependencies are rejected;
- known direct authority shortcuts are rejected (for example NEXUS → MetaPay execution and SynergyNet → Financial OS accounting facts);
- unexpected bidirectional authority/data cycles are rejected;
- the intentional Financial OS ↔ MetaPay request/evidence pair is explicitly allowed;
- architecture and verification vocabularies must remain non-empty and unique.

## Repository completeness

`config/expected_repositories_v1.json` is a frozen inventory checkpoint, not a live GitHub discovery API. When a repository is intentionally added or retired from the active federation, both architecture review and the expected-set generation must change together.

Private-repository live existence checks should be performed by an authenticated external audit job; CI must not require embedding a GitHub credential in the architecture manifest.

## Run

```bash
python -m pip install -e .
python tools/validate_federation.py
python -m pytest -q
```
