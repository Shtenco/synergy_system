from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from synergy_system.service_build_recipe_registry_v1 import (
    EXPECTED_REGISTRY_DIGEST,
    ServiceBuildRecipeRegistryError,
    registry_digest,
    verify_service_build_recipe_registry_v1,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "config" / "service_build_recipe_registry_v1.json"


def _payload() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _rehash(payload: dict) -> dict:
    payload["registry_digest"] = registry_digest(payload)
    return payload


def test_canonical_registry_verifies_and_has_no_build_outputs() -> None:
    payload = verify_service_build_recipe_registry_v1(_payload())
    assert payload["registry_digest"] == EXPECTED_REGISTRY_DIGEST
    assert payload["artifact_digests"] == []
    assert payload["build_evidence_digests"] == []
    assert payload["overall_status"] == "BUILD_RECIPES_FROZEN_ARTIFACTS_NOT_EMITTED"
    assert payload["execution_authority"] == "NONE"


def test_all_science_node_service_ids_are_covered_exactly_once() -> None:
    payload = verify_service_build_recipe_registry_v1(_payload())
    covered = [sid for recipe in payload["recipes"] for sid in recipe["service_ids"]]
    assert sorted(covered) == ["content-cache", "nexus", "science-agent", "synergynet"]
    assert len(covered) == len(set(covered))


def test_missing_service_coverage_is_rejected_even_with_fresh_hash() -> None:
    payload = copy.deepcopy(_payload())
    transport = next(item for item in payload["recipes"] if item["recipe_id"] == "SYNERGYNET_RESEARCH_TRANSPORT_BUILD_RECIPE_V1")
    transport["service_ids"] = ["synergynet"]
    _rehash(payload)
    with pytest.raises(ServiceBuildRecipeRegistryError):
        verify_service_build_recipe_registry_v1(payload)


def test_duplicate_service_coverage_is_rejected_even_with_fresh_hash() -> None:
    payload = copy.deepcopy(_payload())
    nexus = next(item for item in payload["recipes"] if item["recipe_id"] == "NEXUS_SMALLWORLD_SERVICE_BUILD_RECIPE_V1")
    nexus["service_ids"] = ["content-cache", "nexus"]
    _rehash(payload)
    with pytest.raises(ServiceBuildRecipeRegistryError):
        verify_service_build_recipe_registry_v1(payload)


def test_recipe_commit_drift_is_rejected_even_with_fresh_hash() -> None:
    payload = copy.deepcopy(_payload())
    payload["recipes"][0]["recipe_commit"] = "0" * 40
    _rehash(payload)
    with pytest.raises(ServiceBuildRecipeRegistryError):
        verify_service_build_recipe_registry_v1(payload)


def test_fresh_hash_cannot_claim_artifacts_or_build_verified() -> None:
    payload = copy.deepcopy(_payload())
    payload["artifact_digests"] = ["1" * 64]
    payload["build_evidence_digests"] = ["2" * 64]
    payload["overall_status"] = "BUILD_VERIFIED"
    _rehash(payload)
    with pytest.raises(ServiceBuildRecipeRegistryError):
        verify_service_build_recipe_registry_v1(payload)


def test_fresh_hash_cannot_grant_execution_authority() -> None:
    payload = copy.deepcopy(_payload())
    payload["execution_authority"] = "NODE_EXECUTOR"
    _rehash(payload)
    with pytest.raises(ServiceBuildRecipeRegistryError):
        verify_service_build_recipe_registry_v1(payload)
