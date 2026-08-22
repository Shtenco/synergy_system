from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from synergy_system.service_build_recipe_registry_v2 import (
    ServiceBuildRecipeRegistryV2Error,
    canonical_json,
    verify_service_build_recipe_registry_v2,
)


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "service_build_recipe_registry_v2.json"


def _load() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def _rehash(payload: dict) -> None:
    body = dict(payload)
    body.pop("registry_digest", None)
    payload["registry_digest"] = hashlib.sha256(canonical_json(body)).hexdigest()


def test_canonical_registry_v2_is_complete_stdlib_only_and_non_executing() -> None:
    registry = _load()
    assert verify_service_build_recipe_registry_v2(registry) == registry
    assert registry["registry_digest"] == "93b92cb99a38f95b044ec2b3123f37ebf90a603c2768ec47556cf72baa8c7529"
    assert registry["source_build_lock_digest"] == "de35e3f31d85b9ab559180a12535ecdaa58fd70c6d3575d215994064933e1274"
    assert registry["artifact_digests"] == []
    assert registry["build_evidence_digests"] == []
    assert registry["execution_authority"] == "NONE"
    assert all(
        item["dependency_lock_status"] == "STDLIB_ONLY_NO_THIRD_PARTY_RUNTIME_DEPENDENCIES"
        for item in registry["recipes"]
    )


def test_recipe_order_is_canonical_and_service_coverage_exact() -> None:
    registry = _load()
    recipe_ids = [item["recipe_id"] for item in registry["recipes"]]
    assert recipe_ids == sorted(recipe_ids)
    services = [service_id for item in registry["recipes"] for service_id in item["service_ids"]]
    assert sorted(services) == ["content-cache", "nexus", "science-agent", "synergynet"]
    assert len(services) == len(set(services))


def test_nexus_slot_is_exact_v2_recipe_and_source() -> None:
    registry = _load()
    nexus = next(item for item in registry["recipes"] if item["service_ids"] == ["nexus"])
    assert nexus["recipe_id"] == "NEXUS_SMALLWORLD_EXACT_STDLIB_BUILD_RECIPE_V2"
    assert nexus["recipe_schema"] == "nexus.service-build-recipe/v2"
    assert nexus["recipe_commit"] == "d8ef528f1633262d6d5f0b008b1338dd89fcc58b"
    assert nexus["recipe_digest"] == "3e255804dbd420492fc5481fe11d6333be2a50c8834bd4a8e3896de726f44089"
    assert nexus["source_commit"] == "2ee8f2a29ad2497afca6c7386375a296cd0bdbcf"


def test_fresh_hash_cannot_restore_range_only_numpy_recipe() -> None:
    registry = _load()
    nexus = next(item for item in registry["recipes"] if item["service_ids"] == ["nexus"])
    nexus.update({
        "recipe_id": "NEXUS_SMALLWORLD_SERVICE_BUILD_RECIPE_V1",
        "recipe_ref": "feat/smallworld-service-build-recipe-v1-20260821",
        "recipe_commit": "9cf0fc6fb0e6a88f65e0b867682b0afaa3e373d7",
        "recipe_schema": "nexus.service-build-recipe/v1",
        "recipe_digest": "6ec5a878dadf7794f673ef21688e1e0e29d88b534a5f9ac304ee32103b5eb21a",
        "source_commit": "ef1a6e3675e53fda4bf91566aec61f1b62fa9336",
        "dependency_lock_status": "RANGE_ONLY_BLOCKS_BUILD_VERIFICATION",
    })
    registry["recipes"] = sorted(registry["recipes"], key=lambda item: item["recipe_id"])
    _rehash(registry)
    with pytest.raises(ServiceBuildRecipeRegistryV2Error):
        verify_service_build_recipe_registry_v2(registry)


def test_fresh_hash_cannot_claim_artifacts_or_test_evidence() -> None:
    registry = _load()
    registry["artifact_digests"] = ["1" * 64]
    registry["build_evidence_digests"] = ["2" * 64]
    registry["overall_status"] = "BUILD_VERIFIED"
    _rehash(registry)
    with pytest.raises(ServiceBuildRecipeRegistryV2Error):
        verify_service_build_recipe_registry_v2(registry)


def test_duplicate_service_coverage_is_rejected() -> None:
    registry = _load()
    registry["recipes"][0]["service_ids"] = ["science-agent", "synergynet"]
    _rehash(registry)
    with pytest.raises(ServiceBuildRecipeRegistryV2Error):
        verify_service_build_recipe_registry_v2(registry)
