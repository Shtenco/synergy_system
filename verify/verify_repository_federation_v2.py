#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "repository_federation_v2_20260829.json"

EXPECTED_SCHEMA = "synergy.repository-federation/v2"
EXPECTED_COUNT = 42
EXPECTED_OWNER = "Shtenco"
EXPECTED_STEPS = set(range(1, 21))

REQUIRED_REPO_FIELDS = {
    "repository",
    "portfolio_cluster",
    "classification",
    "maturity",
    "role",
    "authority",
    "next_milestone",
    "top20_steps",
}
REQUIRED_POLICY = {
    "historical_evidence_preserved": True,
    "auto_merge": False,
    "merge_authority": "HUMAN_MAINTAINER_ONLY",
    "ai_financial_authority": "NONE",
    "ai_payment_authority": "NONE",
    "ai_accounting_authority": "NONE",
    "ai_blockchain_submission_authority": "NONE",
    "ai_production_deployment_authority": "NONE",
    "status_promotion_requires_executed_evidence": True,
    "internal_mint_or_revaluation_is_external_profit": False,
}


class FederationError(ValueError):
    pass


def _canonical_bytes(obj: Any) -> bytes:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def compute_federation_digest(data: dict[str, Any]) -> str:
    payload = dict(data)
    payload.pop("federation_digest", None)
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def verify_federation(data: dict[str, Any]) -> dict[str, Any]:
    if data.get("schema") != EXPECTED_SCHEMA:
        raise FederationError("schema mismatch")
    if data.get("owner") != EXPECTED_OWNER:
        raise FederationError("owner mismatch")
    if data.get("repository_count") != EXPECTED_COUNT:
        raise FederationError("repository_count mismatch")
    if data.get("policy") != REQUIRED_POLICY:
        raise FederationError("policy mismatch")

    repos = data.get("repositories")
    if not isinstance(repos, list) or len(repos) != EXPECTED_COUNT:
        raise FederationError("repository list length mismatch")

    names: list[str] = []
    covered_steps: set[int] = set()
    for repo in repos:
        if not isinstance(repo, dict):
            raise FederationError("repository entry must be an object")
        if set(repo) != REQUIRED_REPO_FIELDS:
            raise FederationError(f"repository fields mismatch: {repo.get('repository')}")
        name = repo["repository"]
        if not isinstance(name, str) or not name.startswith("Shtenco/"):
            raise FederationError("invalid repository identity")
        names.append(name)

        for field in (
            "portfolio_cluster",
            "classification",
            "maturity",
            "role",
            "authority",
            "next_milestone",
        ):
            value = repo[field]
            if not isinstance(value, str) or not value.strip():
                raise FederationError(f"empty {field}: {name}")

        steps = repo["top20_steps"]
        if not isinstance(steps, list) or not steps:
            raise FederationError(f"missing roadmap steps: {name}")
        if len(steps) != len(set(steps)):
            raise FederationError(f"duplicate roadmap step: {name}")
        for step in steps:
            if not isinstance(step, int) or step not in EXPECTED_STEPS:
                raise FederationError(f"invalid roadmap step: {name}")
            covered_steps.add(step)

    if len(names) != len(set(names)):
        raise FederationError("duplicate repository identity")
    if covered_steps != EXPECTED_STEPS:
        missing = sorted(EXPECTED_STEPS - covered_steps)
        extra = sorted(covered_steps - EXPECTED_STEPS)
        raise FederationError(
            f"roadmap coverage mismatch missing={missing} extra={extra}"
        )

    supplied = data.get("federation_digest")
    computed = compute_federation_digest(data)
    if supplied != computed:
        raise FederationError("federation_digest mismatch")

    return {
        "status": "PASS",
        "schema": EXPECTED_SCHEMA,
        "repository_count": EXPECTED_COUNT,
        "covered_steps": sorted(covered_steps),
        "federation_digest": computed,
        "merge_authority": REQUIRED_POLICY["merge_authority"],
        "auto_merge": False,
    }


def main() -> int:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    print(
        json.dumps(
            verify_federation(data), ensure_ascii=False, indent=2, sort_keys=True
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
