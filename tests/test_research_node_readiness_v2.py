from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

from synergy_system.node_readiness_v2 import (
    NodeReadinessV2Error,
    verify_research_node_readiness_bundle_v2,
)


ROOT = Path(__file__).resolve().parents[1]


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _bundle() -> dict:
    return {
        "readiness": _load("fixtures/node_readiness/research_compute_node_readiness_v2.json"),
        "plan": _load("fixtures/node_build_plans/research_compute_node_build_plan_runtime_services_v2.json"),
        "revision": _load("fixtures/node_source_revisions/research_compute_node_synergynet_runtime_v2.json"),
        "nexus_recipe": _load("fixtures/build_recipes/agi_nexus_build_recipe_v1.json"),
        "synergynet_recipe": _load("fixtures/build_recipes/synergynet_build_recipe_v2.json"),
        "nexus_spec": _load("fixtures/service_specs/agi_nexus_service_spec_v1.json"),
        "content_spec": _load("fixtures/service_specs/content-cache_v2.json"),
        "relay_spec": _load("fixtures/service_specs/synergynet_v2.json"),
    }


def test_readiness_v2_removes_only_evidenced_synergynet_interface_blockers() -> None:
    b = _bundle()
    for fixture, schema_path in (
        (b["revision"], "schemas/synergy_node_source_revision_v1.schema.json"),
        (b["plan"], "schemas/synergy_node_build_plan_v2.schema.json"),
        (b["readiness"], "schemas/synergy_node_readiness_v2.schema.json"),
    ):
        jsonschema.validate(fixture, _load(schema_path))
    verified = verify_research_node_readiness_bundle_v2(**b)
    assert verified["blockers"] == [
        "BUILD_ARTIFACTS_NOT_VERIFIED",
        "BUILD_TOOLCHAIN_NOT_FROZEN",
        "NEXUS_SERVICE_INTERFACE_NOT_IMPLEMENTED",
    ]
    assert verified["resolved_since_v1"] == [
        "CONTENT_CACHE_SERVICE_INTERFACE_NOT_IMPLEMENTED",
        "SYNERGYNET_SERVICE_INTERFACE_NOT_IMPLEMENTED",
    ]
    assert verified["node_status"] == "NODE_NOT_DEPLOYABLE"
    assert verified["execution_authority"] == "NONE"


def test_fresh_hash_cannot_remove_nexus_blocker() -> None:
    b = _bundle()
    b["readiness"] = copy.deepcopy(b["readiness"])
    b["readiness"]["blockers"] = ["BUILD_ARTIFACTS_NOT_VERIFIED", "BUILD_TOOLCHAIN_NOT_FROZEN"]
    with pytest.raises(NodeReadinessV2Error):
        verify_research_node_readiness_bundle_v2(**b)


def test_fresh_hash_cannot_claim_synergynet_artifact() -> None:
    b = _bundle()
    b["synergynet_recipe"] = copy.deepcopy(b["synergynet_recipe"])
    b["synergynet_recipe"]["artifact_digest"] = "1" * 64
    with pytest.raises(NodeReadinessV2Error):
        verify_research_node_readiness_bundle_v2(**b)


def test_runtime_source_and_build_source_hash_domains_cannot_be_swapped() -> None:
    b = _bundle()
    b["revision"] = copy.deepcopy(b["revision"])
    b["revision"]["services"][0]["runtime_source_commit"] = b["revision"]["services"][0]["build_source_commit"]
    with pytest.raises(NodeReadinessV2Error):
        verify_research_node_readiness_bundle_v2(**b)


def test_old_library_only_synergynet_spec_cannot_satisfy_v2_interface() -> None:
    b = _bundle()
    b["content_spec"] = _load("fixtures/service_specs/synergynet_content_cache_service_spec_v1.json")
    with pytest.raises(NodeReadinessV2Error):
        verify_research_node_readiness_bundle_v2(**b)
