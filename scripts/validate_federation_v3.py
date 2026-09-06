#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "repository_federation_v3.yaml"


def fail(msg: str) -> None:
    raise AssertionError(msg)


def main() -> int:
    data: dict[str, Any] = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))

    if data.get("schema") != "synergy.repository-federation/v3":
        fail("unexpected schema")

    repos = data.get("repositories") or []
    expected = int(data.get("observed_repository_count", -1))
    if len(repos) != expected:
        fail(f"repository count mismatch: config says {expected}, list has {len(repos)}")
    if expected != 45:
        fail(f"Federation V3 must currently enumerate 45 observed repositories, got {expected}")

    names = [r.get("repo") for r in repos]
    if any(not n for n in names):
        fail("every repository must have repo")
    if len(set(names)) != len(names):
        dupes = sorted({n for n in names if names.count(n) > 1})
        fail(f"duplicate repository entries: {dupes}")

    required = {"repo", "layer", "class", "role", "authority", "origin"}
    for r in repos:
        missing = required - set(r)
        if missing:
            fail(f"{r.get('repo')}: missing fields {sorted(missing)}")
        if not isinstance(r["origin"], list) or not r["origin"]:
            fail(f"{r['repo']}: origin must be a non-empty list")

    repo_set = set(names)
    deps = data.get("canonical_dependency_direction") or []
    for d in deps:
        for endpoint in ("from", "to"):
            if d.get(endpoint) not in repo_set:
                fail(f"dependency endpoint missing from federation: {d}")
        if not d.get("contract"):
            fail(f"dependency missing contract: {d}")

    authorities = data.get("exclusive_authorities") or {}
    for authority_name, repo in authorities.items():
        if repo not in repo_set:
            fail(f"exclusive authority {authority_name} points outside federation: {repo}")

    constitution = data.get("constitution") or {}
    mandatory_true = [
        "federation_not_monorepo",
        "one_authority_per_fact",
        "evidence_before_claim",
        "external_settlement_before_external_profit",
        "ai_is_not_execution_authority",
        "blockchain_is_not_accounting_authority",
        "presentation_is_not_authority",
        "network_growth_must_be_value_backed",
        "recruitment_is_not_revenue",
        "scientific_hypothesis_is_not_scientific_truth",
    ]
    for key in mandatory_true:
        if constitution.get(key) is not True:
            fail(f"constitution invariant must be true: {key}")

    levels = data.get("origin_levels") or {}
    required_levels = {
        "L1_PERSONAL_CAPITAL",
        "L2_NETWORK_BUSINESS",
        "L3_CAPITAL_FINANCE",
        "L4_SCIENCE",
        "L5_INDUSTRY_REGIONS",
        "L6_AI_GOVERNANCE",
        "MONETARY_PAYMENT_LAYER",
    }
    if not required_levels.issubset(levels):
        fail(f"missing origin levels: {sorted(required_levels - set(levels))}")

    print(f"PASS Federation V3: {len(repos)} repositories, {len(deps)} dependency contracts, {len(authorities)} exclusive authorities")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL Federation V3: {exc}", file=sys.stderr)
        raise SystemExit(1)
