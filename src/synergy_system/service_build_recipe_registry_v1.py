from __future__ import annotations

import hashlib
import json
import re
from typing import Any


class ServiceBuildRecipeRegistryError(ValueError):
    pass


HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

EXPECTED_REGISTRY_DIGEST = "afbd333f3dc792287c0bab18a5bbb604be139feb6ea41f48a9af352203f039f6"
EXPECTED_PROFILE_DIGEST = "0c9b82e591c5aa30d1f9b499edee02c0b56643af825bbb7eecb93f8651659107"
EXPECTED_CAPABILITY_REGISTRY_DIGEST = "3727810480e5660129fc63a2d7999b988ed9ae387365d4501bb50b7ae7257913"
EXPECTED_SOURCE_BUILD_LOCK_DIGEST = "24e4a3c6ed23c2e156b07821fb3b1e0e232651c256bc3b750d2ed25bee477757"
EXPECTED_SERVICE_IDS = {"content-cache", "nexus", "science-agent", "synergynet"}

EXPECTED_RECIPES = {
    "NEXUS_SMALLWORLD_SERVICE_BUILD_RECIPE_V1": {
        "repository": "Shtenco/agi_nexus",
        "recipe_ref": "feat/smallworld-service-build-recipe-v1-20260821",
        "recipe_commit": "9cf0fc6fb0e6a88f65e0b867682b0afaa3e373d7",
        "recipe_schema": "nexus.service-build-recipe/v1",
        "recipe_digest": "6ec5a878dadf7794f673ef21688e1e0e29d88b534a5f9ac304ee32103b5eb21a",
        "service_ids": ["nexus"],
        "source_commit": "ef1a6e3675e53fda4bf91566aec61f1b62fa9336",
        "dependency_lock_status": "RANGE_ONLY_BLOCKS_BUILD_VERIFICATION",
        "build_status": "RECIPE_DEFINED_ARTIFACT_NOT_EMITTED",
    },
    "NEXUS_SCIENCE_LOCAL_SERVICE_BUILD_RECIPE_V1": {
        "repository": "Shtenco/nexus_science_agent",
        "recipe_ref": "feat/local-science-service-build-recipe-v1-20260821",
        "recipe_commit": "2e4e86484d842f1283204fa87d86927603278e5b",
        "recipe_schema": "nexus-science.service-build-recipe/v1",
        "recipe_digest": "3b1f7a64a943a0a144a52ead894c1e0c2d454e67657992ebcb434a6fdcd18c78",
        "service_ids": ["science-agent"],
        "source_commit": "0607690c3036d2fdce2ac3e044094a8e4da0311b",
        "dependency_lock_status": "STDLIB_ONLY_NO_THIRD_PARTY_RUNTIME_DEPENDENCIES",
        "build_status": "RECIPE_DEFINED_ARTIFACT_NOT_EMITTED",
    },
    "SYNERGYNET_RESEARCH_TRANSPORT_BUILD_RECIPE_V1": {
        "repository": "Shtenco/synergynet",
        "recipe_ref": "feat/research-transport-build-recipe-v1-20260821",
        "recipe_commit": "a187551e121350edf690d7570ca4dc76f749d17f",
        "recipe_schema": "synergynet.service-build-recipe/v1",
        "recipe_digest": "16d3456cddfd9b6e6f876967aac67b8d54b58b6ff6d997a33163feb12daa8792",
        "service_ids": ["content-cache", "synergynet"],
        "source_commit": "874a83b6510420ec43ce99fc4b7936e106ad2339",
        "dependency_lock_status": "STDLIB_ONLY_NO_THIRD_PARTY_RUNTIME_DEPENDENCIES",
        "build_status": "RECIPE_DEFINED_ARTIFACT_NOT_EMITTED",
    },
}


def canonical_json(value: Any) -> bytes:
    def check(item: Any) -> None:
        if item is None or isinstance(item, (str, bool)):
            return
        if isinstance(item, int) and not isinstance(item, bool):
            if abs(item) > 2**53 - 1:
                raise ServiceBuildRecipeRegistryError("unsafe integer")
            return
        if isinstance(item, float):
            raise ServiceBuildRecipeRegistryError("floats forbidden in registry bytes")
        if isinstance(item, list):
            for child in item:
                check(child)
            return
        if isinstance(item, dict):
            if any(not isinstance(key, str) for key in item):
                raise ServiceBuildRecipeRegistryError("object keys must be strings")
            for child in item.values():
                check(child)
            return
        raise ServiceBuildRecipeRegistryError(f"unsupported value: {type(item)!r}")

    check(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def registry_digest(payload: dict[str, Any]) -> str:
    body = dict(payload)
    body.pop("registry_digest", None)
    return hashlib.sha256(canonical_json(body)).hexdigest()


def _require_hex(value: Any, regex: re.Pattern[str], label: str) -> str:
    if not isinstance(value, str) or not regex.fullmatch(value):
        raise ServiceBuildRecipeRegistryError(f"{label} has invalid digest/commit format")
    return value


def verify_service_build_recipe_registry_v1(payload: dict[str, Any]) -> dict[str, Any]:
    expected_shape = {
        "schema",
        "registry_id",
        "node_profile_digest",
        "capability_registry_digest",
        "source_build_lock_digest",
        "recipes",
        "artifact_digests",
        "build_evidence_digests",
        "overall_status",
        "authority",
        "execution_authority",
        "registry_digest",
    }
    if not isinstance(payload, dict) or set(payload) != expected_shape:
        raise ServiceBuildRecipeRegistryError("unexpected recipe registry shape")
    if payload["schema"] != "synergy.service-build-recipe-registry/v1":
        raise ServiceBuildRecipeRegistryError("unexpected recipe registry schema")
    if payload["registry_id"] != "SCIENCE_RESEARCH_NODE_BUILD_RECIPES_20260821":
        raise ServiceBuildRecipeRegistryError("unexpected registry generation")

    _require_hex(payload["node_profile_digest"], HEX64, "node_profile_digest")
    _require_hex(payload["capability_registry_digest"], HEX64, "capability_registry_digest")
    _require_hex(payload["source_build_lock_digest"], HEX64, "source_build_lock_digest")
    _require_hex(payload["registry_digest"], HEX64, "registry_digest")

    if payload["node_profile_digest"] != EXPECTED_PROFILE_DIGEST:
        raise ServiceBuildRecipeRegistryError("node profile digest drift")
    if payload["capability_registry_digest"] != EXPECTED_CAPABILITY_REGISTRY_DIGEST:
        raise ServiceBuildRecipeRegistryError("capability registry digest drift")
    if payload["source_build_lock_digest"] != EXPECTED_SOURCE_BUILD_LOCK_DIGEST:
        raise ServiceBuildRecipeRegistryError("source build-lock digest drift")

    if payload["artifact_digests"] != [] or payload["build_evidence_digests"] != []:
        raise ServiceBuildRecipeRegistryError("v1 current generation cannot claim emitted build artifacts/evidence")
    if payload["overall_status"] != "BUILD_RECIPES_FROZEN_ARTIFACTS_NOT_EMITTED":
        raise ServiceBuildRecipeRegistryError("v1 current generation cannot claim build completion")
    if payload["authority"] != "BUILD_ORCHESTRATION_METADATA_ONLY":
        raise ServiceBuildRecipeRegistryError("registry authority drift")
    if payload["execution_authority"] != "NONE":
        raise ServiceBuildRecipeRegistryError("recipe registry cannot execute services")

    recipes = payload["recipes"]
    if not isinstance(recipes, list) or len(recipes) != len(EXPECTED_RECIPES):
        raise ServiceBuildRecipeRegistryError("unexpected recipe count")

    seen_recipe_ids: set[str] = set()
    covered_services: set[str] = set()
    for recipe in recipes:
        fields = {
            "recipe_id",
            "repository",
            "recipe_ref",
            "recipe_commit",
            "recipe_schema",
            "recipe_digest",
            "service_ids",
            "source_commit",
            "dependency_lock_status",
            "build_status",
        }
        if not isinstance(recipe, dict) or set(recipe) != fields:
            raise ServiceBuildRecipeRegistryError("unexpected recipe entry shape")
        recipe_id = recipe["recipe_id"]
        if not isinstance(recipe_id, str) or recipe_id in seen_recipe_ids:
            raise ServiceBuildRecipeRegistryError("recipe_id must be unique")
        seen_recipe_ids.add(recipe_id)
        expected = EXPECTED_RECIPES.get(recipe_id)
        if expected is None:
            raise ServiceBuildRecipeRegistryError("unknown recipe id")

        _require_hex(recipe["recipe_commit"], HEX40, "recipe_commit")
        _require_hex(recipe["source_commit"], HEX40, "source_commit")
        _require_hex(recipe["recipe_digest"], HEX64, "recipe_digest")

        for key, expected_value in expected.items():
            if recipe[key] != expected_value:
                raise ServiceBuildRecipeRegistryError(f"recipe semantic drift: {recipe_id}:{key}")

        service_ids = recipe["service_ids"]
        if not isinstance(service_ids, list) or service_ids != sorted(service_ids) or len(service_ids) != len(set(service_ids)):
            raise ServiceBuildRecipeRegistryError("service_ids must be sorted and unique")
        for service_id in service_ids:
            if service_id in covered_services:
                raise ServiceBuildRecipeRegistryError("service is covered by more than one recipe")
            covered_services.add(service_id)

    if seen_recipe_ids != set(EXPECTED_RECIPES):
        raise ServiceBuildRecipeRegistryError("recipe coverage incomplete")
    if covered_services != EXPECTED_SERVICE_IDS:
        raise ServiceBuildRecipeRegistryError("Science Node service coverage mismatch")

    calculated = registry_digest(payload)
    if calculated != payload["registry_digest"]:
        raise ServiceBuildRecipeRegistryError("registry digest mismatch")
    if payload["registry_digest"] != EXPECTED_REGISTRY_DIGEST:
        raise ServiceBuildRecipeRegistryError("unexpected canonical registry digest")

    canonical_json(payload)
    return payload
