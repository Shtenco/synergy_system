from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from synergy_system.node_readiness_v3 import NodeReadinessV3Error, verify_readiness_v3


ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def bundle() -> dict:
    return {
        "readiness": load("fixtures/node_readiness/research_compute_node_readiness_v3.json"),
        "plan": load("fixtures/node_build_plans/research_compute_node_build_plan_all_interfaces_v3.json"),
        "revision": load("fixtures/node_source_revisions/research_compute_node_nexus_proof_core_v2.json"),
        "nexus_recipe": load("fixtures/build_recipes/agi_nexus_build_recipe_v2.json"),
        "nexus_spec": load("fixtures/service_specs/agi_nexus_service_spec_v2.json"),
    }


def test_v3_resolves_last_service_interface_blocker_only() -> None:
    b = bundle()
    verified = verify_readiness_v3(**b)
    assert verified["service_status"] == "ALL_REQUIRED_SERVICE_INTERFACES_IMPLEMENTED_SOURCE_ONLY"
    assert verified["blockers"] == ["BUILD_ARTIFACTS_NOT_VERIFIED", "BUILD_TOOLCHAIN_NOT_FROZEN"]
    assert verified["resolved_since_v2"] == ["NEXUS_SERVICE_INTERFACE_NOT_IMPLEMENTED"]
    assert verified["node_status"] == "NODE_NOT_DEPLOYABLE"
    assert verified["execution_authority"] == "NONE"


def test_fresh_hash_cannot_remove_build_blockers() -> None:
    b = bundle()
    b["readiness"] = copy.deepcopy(b["readiness"])
    b["readiness"]["blockers"] = []
    with pytest.raises(NodeReadinessV3Error):
        verify_readiness_v3(**b)


def test_old_library_nexus_status_cannot_reappear_as_implemented() -> None:
    b = bundle()
    b["revision"] = copy.deepcopy(b["revision"])
    b["revision"]["services"][1]["interface_status"] = "SERVICE_INTERFACE_NOT_IMPLEMENTED"
    with pytest.raises(NodeReadinessV3Error):
        verify_readiness_v3(**b)


def test_nexus_build_artifact_overclaim_is_rejected() -> None:
    b = bundle()
    b["nexus_recipe"] = copy.deepcopy(b["nexus_recipe"])
    b["nexus_recipe"]["artifact_digest"] = "1" * 64
    with pytest.raises(NodeReadinessV3Error):
        verify_readiness_v3(**b)


def test_fake_neural_readiness_is_rejected_at_service_evidence() -> None:
    b = bundle()
    b["nexus_spec"] = copy.deepcopy(b["nexus_spec"])
    b["nexus_spec"]["neural_hypothesis_status"] = "OMEGA_R5_PRODUCTION_READY"
    with pytest.raises(NodeReadinessV3Error):
        verify_readiness_v3(**b)
