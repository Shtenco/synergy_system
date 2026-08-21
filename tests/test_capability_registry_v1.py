from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from synergy_system.capability_registry_v1 import CapabilityRegistryError, validate_capability_registry_v1


FIXTURE = Path("fixtures/capabilities/synergy_capability_registry_v1.json")
EXPECTED_DIGEST = "3727810480e5660129fc63a2d7999b988ed9ae387365d4501bb50b7ae7257913"


def load_fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_canonical_registry_digest_and_new_roles():
    payload = load_fixture()
    assert validate_capability_registry_v1(payload) == EXPECTED_DIGEST
    caps = {item["capability_id"] for item in payload["capabilities"]}
    assert {"SCIENCE_RESEARCH", "MIDAS_ANALYSIS"}.issubset(caps)


def test_capability_cannot_grant_authority_even_with_fresh_payload():
    payload = load_fixture()
    payload["capabilities"][0]["authority_grant"] = "EXECUTE"
    with pytest.raises(CapabilityRegistryError):
        validate_capability_registry_v1(payload)


def test_unknown_required_capability_fails_closed():
    payload = load_fixture()
    payload["service_kinds"][0]["required_capabilities"] = ["UNKNOWN_CAP"]
    with pytest.raises(CapabilityRegistryError):
        validate_capability_registry_v1(payload)


def test_order_is_part_of_canonical_contract():
    payload = load_fixture()
    payload["capabilities"] = list(reversed(payload["capabilities"]))
    with pytest.raises(CapabilityRegistryError):
        validate_capability_registry_v1(payload)


def test_registry_is_immutable_under_copy():
    original = load_fixture()
    clone = copy.deepcopy(original)
    assert validate_capability_registry_v1(original) == validate_capability_registry_v1(clone)
