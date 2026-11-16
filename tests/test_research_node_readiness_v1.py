from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import jsonschema
import pytest

from synergy_system.node_readiness_v1 import NodeReadinessError, canonical_json, verify_research_node_readiness_v1


ROOT = Path(__file__).resolve().parents[1]


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text())


def _readiness() -> dict:
    return _load("fixtures/node_readiness/research_compute_node_readiness_v1.json")


def _build_plan() -> dict:
    return _load("fixtures/node_build_plans/research_compute_node_build_plan_source_candidate_v1.json")


def _service_specs() -> dict[str, dict]:
    return {
        "content-cache": _load("fixtures/service_specs/synergynet_content_cache_service_spec_v1.json"),
        "nexus": _load("fixtures/service_specs/agi_nexus_service_spec_v1.json"),
        "synergynet": _load("fixtures/service_specs/synergynet_transport_service_spec_v1.json"),
    }


def test_current_research_node_is_explicitly_not_deployable() -> None:
    decision = verify_research_node_readiness_v1(_readiness(), _build_plan(), _service_specs())
    assert decision.status == "NODE_NOT_DEPLOYABLE"
    assert decision.deployable is False
    assert decision.build_plan_verified is True
    assert decision.service_specs_verified is True


def test_readiness_fixture_matches_wire_schema() -> None:
    schema = _load("schemas/synergy_node_readiness_v1.schema.json")
    jsonschema.validate(_readiness(), schema)


def test_fresh_hash_cannot_remove_blockers_or_claim_deployable() -> None:
    readiness = copy.deepcopy(_readiness())
    readiness["build_status"] = "BUILD_VERIFIED"
    readiness["service_status"] = "SERVICE_INTERFACES_READY"
    readiness["node_status"] = "DEPLOYABLE"
    readiness["blockers"] = []
    body = dict(readiness)
    body.pop("readiness_digest", None)
    readiness["readiness_digest"] = hashlib.sha256(canonical_json(body)).hexdigest()
    with pytest.raises(NodeReadinessError):
        verify_research_node_readiness_v1(readiness, _build_plan(), _service_specs())


def test_self_consistent_service_spec_upgrade_is_wrong_generation() -> None:
    specs = _service_specs()
    spec = copy.deepcopy(specs["nexus"])
    spec["runtime_form"] = "PYTHON_SERVICE"
    spec["entrypoint"] = "agi_nexus.runtime:main"
    spec["health_probe"] = "HEALTH_V1"
    spec["lifecycle_protocol"] = "META_OS_SERVICE_V1"
    spec["wire_protocol"] = "NEXUS_RPC_V1"
    spec["readiness_status"] = "RUNNABLE"
    body = dict(spec)
    body.pop("spec_digest", None)
    spec["spec_digest"] = hashlib.sha256(canonical_json(body)).hexdigest()
    specs["nexus"] = spec
    with pytest.raises(NodeReadinessError):
        verify_research_node_readiness_v1(_readiness(), _build_plan(), specs)
