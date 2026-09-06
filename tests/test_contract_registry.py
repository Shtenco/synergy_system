from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_contract_registry_is_unique_and_resolvable():
    registry = json.loads((ROOT / "config" / "contract_registry_v1.json").read_text(encoding="utf-8"))
    entries = registry["contracts"]
    types = [entry["type"] for entry in entries]
    assert len(types) == len(set(types)), "contract types must be globally unique"
    for entry in entries:
        assert (ROOT / "schemas" / entry["schema"]).exists(), f"missing schema for {entry['type']}"
        assert entry["producer"].startswith("Shtenco/")
        assert entry["producer_authority"]
        assert entry["consumer_authority"]


def test_v1_compatibility_policy_protects_core_authority_invariants():
    compatibility = json.loads((ROOT / "config" / "contract_compatibility_v1.json").read_text(encoding="utf-8"))
    policy = compatibility["policy"]
    forbidden = set(policy["forbidden_without_constitution_change"])
    assert policy["current_major"] == 1
    assert policy["v1_semantics_immutable"] is True
    assert "grant_execution_authority_to_nexus" in forbidden
    assert "grant_accounting_authority_to_blockchain" in forbidden
    assert "recognize_internal_mark_change_as_external_profit" in forbidden


def test_supported_chain_set_matches_v1_schema_set():
    compatibility = json.loads((ROOT / "config" / "contract_compatibility_v1.json").read_text(encoding="utf-8"))
    supported = set(compatibility["supported_chains"])
    expected = {
        "nexus_autopilot",
        "midas_metapay_financial",
        "science_eurasian_financial",
        "budget_metapay_financial",
        "financial_blockchain_metachain",
    }
    assert supported == expected
    assert all(meta["major"] == 1 for meta in compatibility["supported_chains"].values())
