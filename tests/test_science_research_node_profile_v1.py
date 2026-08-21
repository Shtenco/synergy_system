from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from synergy_system.node_profile_v1 import NodeProfileError
from synergy_system.science_node_profile_v1 import verify_science_research_profile


FIXTURE = Path("fixtures/node_profiles/science_research_node_v1.json")
REPOS = {"Shtenco/synergynet", "Shtenco/agi_nexus", "Shtenco/nexus_science_agent"}


def load_fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_science_profile_is_exact_and_non_financial():
    payload = verify_science_research_profile(load_fixture(), expected_repositories=REPOS)
    assert payload["profile_digest"] == "0c9b82e591c5aa30d1f9b499edee02c0b56643af825bbb7eecb93f8651659107"
    assert payload["financial_authority"] == "NONE"
    assert payload["payment_authority"] == "NONE"
    assert payload["accounting_authority"] == "NONE"
    assert payload["execution_authority"] == "NONE"


def test_metapay_escalation_is_forbidden_even_if_profile_is_rehashed_elsewhere():
    payload = load_fixture()
    payload["allowed_capabilities"].append("METAPAY_GATEWAY")
    payload["allowed_capabilities"].sort()
    with pytest.raises(NodeProfileError):
        verify_science_research_profile(payload, expected_repositories=REPOS)


def test_midas_service_is_not_part_of_science_node_v1():
    payload = copy.deepcopy(load_fixture())
    payload["required_services"].append({"service_id":"midas","kind":"MIDAS","repository":"Shtenco/midas_ai","required_capabilities":["MIDAS_ANALYSIS"]})
    payload["required_services"] = sorted(payload["required_services"], key=lambda x:x["service_id"])
    with pytest.raises(NodeProfileError):
        verify_science_research_profile(payload, expected_repositories=REPOS | {"Shtenco/midas_ai"})


def test_science_agent_repository_is_fixed():
    payload = load_fixture()
    for service in payload["required_services"]:
        if service["service_id"] == "science-agent":
            service["repository"] = "Shtenco/agi_nexus"
    with pytest.raises(NodeProfileError):
        verify_science_research_profile(payload, expected_repositories=REPOS)
