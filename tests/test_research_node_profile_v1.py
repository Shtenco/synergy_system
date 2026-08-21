import json
from pathlib import Path

import pytest

from synergy_system.node_profile_v1 import NodeProfileError, profile_digest, verify_research_compute_profile

ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def expected_repositories():
    return set(load_json("config/expected_repositories_v1.json")["repositories"])


def test_canonical_research_profile_has_fixed_digest_and_no_authority():
    payload = load_json("fixtures/node_profiles/research_compute_node_v1.json")
    verify_research_compute_profile(payload, expected_repositories=expected_repositories())
    assert profile_digest(payload) == "406740705e853fa51ad4eacf7a01925fbe4b5cec491be35ea12ba777d217d714"
    assert payload["financial_authority"] == payload["payment_authority"] == payload["accounting_authority"] == "NONE"
    assert payload["execution_authority"] == "NONE"


def test_financial_service_or_capability_escalation_is_rejected_even_with_fresh_digest():
    payload = load_json("fixtures/node_profiles/research_compute_node_v1.json")
    payload["required_services"].append({
        "service_id":"metapay", "kind":"METAPAY", "repository":"Shtenco/synergy_pay_system",
        "required_capabilities":["METAPAY_GATEWAY"]
    })
    payload["allowed_capabilities"].append("METAPAY_GATEWAY")
    payload["allowed_capabilities"].sort()
    payload["required_services"] = sorted(payload["required_services"], key=lambda item: item["service_id"])
    payload["profile_digest"] = profile_digest(payload)
    with pytest.raises(NodeProfileError):
        verify_research_compute_profile(payload, expected_repositories=expected_repositories())


def test_authority_escalation_is_rejected_with_fresh_digest():
    payload = load_json("fixtures/node_profiles/research_compute_node_v1.json")
    payload["payment_authority"] = "METAPAY"
    payload["profile_digest"] = profile_digest(payload)
    with pytest.raises(NodeProfileError, match="payment_authority"):
        verify_research_compute_profile(payload, expected_repositories=expected_repositories())


def test_schema_overlay_registers_only_system_to_meta_os_contract():
    overlay = load_json("config/cross_repo_schema_overlay_node_profile_v1.json")
    assert overlay["schema"] == "synergy.cross-repo-schema-overlay/v1"
    assert overlay["additions"] == [{
        "id":"synergy.node-profile/v1",
        "producer":"Shtenco/synergy_system",
        "consumers":["Shtenco/synergy_meta_os"],
        "status":"CURRENT_DRAFT",
        "visibility":"FEDERATION"
    }]
    assert overlay["execution_authority"] == "NONE"
