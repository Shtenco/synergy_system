from __future__ import annotations

import hashlib
import json
import re
from typing import Any


class ServiceBuildRecipeRegistryV2Error(ValueError):
    pass


HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_REGISTRY_DIGEST = "93b92cb99a38f95b044ec2b3123f37ebf90a603c2768ec47556cf72baa8c7529"
EXPECTED_PROFILE_DIGEST = "0c9b82e591c5aa30d1f9b499edee02c0b56643af825bbb7eecb93f8651659107"
EXPECTED_CAPABILITY_REGISTRY_DIGEST = "3727810480e5660129fc63a2d7999b988ed9ae387365d4501bb50b7ae7257913"
EXPECTED_SOURCE_BUILD_LOCK_DIGEST = "de35e3f31d85b9ab559180a12535ecdaa58fd70c6d3575d215994064933e1274"
EXPECTED_SERVICE_IDS = {"content-cache", "nexus", "science-agent", "synergynet"}
STDLIB_LOCK_STATUS = "STDLIB_ONLY_NO_THIRD_PARTY_RUNTIME_DEPENDENCIES"

EXPECTED_RECIPES = {
    "NEXUS_SMALLWORLD_EXACT_STDLIB_BUILD_RECIPE_V2": {
        "repository": "Shtenco/agi_nexus",
        "recipe_ref": "feat/smallworld-exact-build-recipe-v2-20260822",
        "recipe_commit": "d8ef528f1633262d6d5f0b008b1338dd89fcc58b",
        "recipe_schema": "nexus.service-build-recipe/v2",
        "recipe_digest": "3e255804dbd420492fc5481fe11d6333be2a50c8834bd4a8e3896de726f44089",
        "service_ids": ["nexus"],
        "source_commit": "2ee8f2a29ad2497afca6c7386375a296cd0bdbcf",
        "dependency_lock_status": STDLIB_LOCK_STATUS,
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
        "dependency_lock_status": STDLIB_LOCK_STATUS,
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
        "dependency_lock_status": STDLIB_LOCK_STATUS,
        "build_status": "RECIPE_DEFINED_ARTIFACT_NOT_EMITTED",
    },
}


def canonical_json(value: Any) -> bytes:
    def check(item: Any) -> None:
        if item is None or isinstance(item, (str, bool)):
            return
        if isinstance(item, int) and not isinstance(item, bool):
            if abs(item) > 2**53 - 1:
                raise ServiceBuildRecipeRegistryV2Error("unsafe integer")
            return
        if isinstance(item, float):
            raise ServiceBuildRecipeRegistryV2Error("floats forbidden in registry bytes")
        if isinstance(item, list):
            for child in item:
                check(child)
            return
        if isinstance(item, dict):
            if any(not isinstance(key, str) for key in item):
                raise ServiceBuildRecipeRegistryV2Error("object keys must be strings")
            for child in item.values():
                check(child)
            return
        raise ServiceBuildRecipeRegistryV2Error(f"unsupported registry value: {type(item)!r}")

    check(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def registry_digest(payload: dict[str, Any]) -> str:
    body = dict(payload)
    body.pop("registry_digest", None)
    return hashlib.sha256(canonical_json(body)).hexdigest()


def _hex(value: Any, pattern: re.Pattern[str], label: str) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise ServiceBuildRecipeRegistryV2Error(f"invalid {label}")
    return value


def verify_service_build_recipe_registry_v2(payload: dict[str, Any]) -> dict[str, Any]:
    expected_shape = {
        "schema", "registry_id", "node_profile_digest", "capability_registry_digest",
        "source_build_lock_digest", "recipes", "artifact_digests", "build_evidence_digests",
        "overall_status", "authority", "execution_authority", "registry_digest",
    }
    if not isinstance(payload, dict) or set(payload) != expected_shape:
        raise ServiceBuildRecipeRegistryV2Error("unexpected recipe registry v2 shape")
    if payload["schema"] != "synergy.service-build-recipe-registry/v2":
        raise ServiceBuildRecipeRegistryV2Error("unexpected registry schema")
    if payload["registry_id"] != "SCIENCE_RESEARCH_NODE_BUILD_RECIPES_20260822":
        raise ServiceBuildRecipeRegistryV2Error("unexpected registry generation")
    if payload["node_profile_digest"] != EXPECTED_PROFILE_DIGEST:
        raise ServiceBuildRecipeRegistryV2Error("node profile digest drift")
    if payload["capability_registry_digest"] != EXPECTED_CAPABILITY_REGISTRY_DIGEST:
        raise ServiceBuildRecipeRegistryV2Error("capability registry digest drift")
    if payload["source_build_lock_digest"] != EXPECTED_SOURCE_BUILD_LOCK_DIGEST:
        raise ServiceBuildRecipeRegistryV2Error("source build-lock digest drift")
    for field in ("node_profile_digest", "capability_registry_digest", "source_build_lock_digest", "registry_digest"):
        _hex(payload[field], HEX64, field)

    if payload["artifact_digests"] != [] or payload["build_evidence_digests"] != []:
        raise ServiceBuildRecipeRegistryV2Error("v2 registry cannot pre-claim artifact/test evidence")
    if payload["overall_status"] != "BUILD_RECIPES_FROZEN_ARTIFACTS_NOT_EMITTED":
        raise ServiceBuildRecipeRegistryV2Error("v2 registry overclaims build completion")
    if payload["authority"] != "BUILD_ORCHESTRATION_METADATA_ONLY":
        raise ServiceBuildRecipeRegistryV2Error("registry authority drift")
    if payload["execution_authority"] != "NONE":
        raise ServiceBuildRecipeRegistryV2Error("registry cannot execute services")

    recipes = payload["recipes"]
    if not isinstance(recipes, list) or len(recipes) != len(EXPECTED_RECIPES):
        raise ServiceBuildRecipeRegistryV2Error("unexpected recipe count")
    recipe_ids = [item.get("recipe_id") for item in recipes if isinstance(item, dict)]
    if recipe_ids != sorted(recipe_ids):
        raise ServiceBuildRecipeRegistryV2Error("recipes must be sorted by recipe_id")

    seen: set[str] = set()
    covered_services: set[str] = set()
    for recipe in recipes:
        fields = {
            "recipe_id", "repository", "recipe_ref", "recipe_commit", "recipe_schema",
            "recipe_digest", "service_ids", "source_commit", "dependency_lock_status", "build_status",
        }
        if not isinstance(recipe, dict) or set(recipe) != fields:
            raise ServiceBuildRecipeRegistryV2Error("unexpected recipe entry shape")
        recipe_id = recipe["recipe_id"]
        if not isinstance(recipe_id, str) or recipe_id in seen:
            raise ServiceBuildRecipeRegistryV2Error("recipe id must be unique")
        seen.add(recipe_id)
        expected = EXPECTED_RECIPES.get(recipe_id)
        if expected is None:
            raise ServiceBuildRecipeRegistryV2Error("unknown recipe id")
        _hex(recipe["recipe_commit"], HEX40, "recipe commit")
        _hex(recipe["source_commit"], HEX40, "source commit")
        _hex(recipe["recipe_digest"], HEX64, "recipe digest")
        for field, expected_value in expected.items():
            if recipe[field] != expected_value:
                raise ServiceBuildRecipeRegistryV2Error(f"recipe semantic drift: {recipe_id}:{field}")
        if recipe["dependency_lock_status"] != STDLIB_LOCK_STATUS:
            raise ServiceBuildRecipeRegistryV2Error("all v2 Science Node recipes must be stdlib-only")
        service_ids = recipe["service_ids"]
        if not isinstance(service_ids, list) or service_ids != sorted(set(service_ids)):
            raise ServiceBuildRecipeRegistryV2Error("service ids must be sorted and unique")
        for service_id in service_ids:
            if service_id in covered_services:
                raise ServiceBuildRecipeRegistryV2Error("service covered by multiple recipes")
            covered_services.add(service_id)

    if seen != set(EXPECTED_RECIPES):
        raise ServiceBuildRecipeRegistryV2Error("recipe coverage incomplete")
    if covered_services != EXPECTED_SERVICE_IDS:
        raise ServiceBuildRecipeRegistryV2Error("Science Node service coverage mismatch")
    calculated = registry_digest(payload)
    if calculated != payload["registry_digest"] or calculated != EXPECTED_REGISTRY_DIGEST:
        raise ServiceBuildRecipeRegistryV2Error("canonical registry digest mismatch")
    canonical_json(payload)
    return payload
