from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any

from synergy_system.node_build_plan_v1 import verify_research_node_build_plan_v1


class NodeReadinessError(ValueError):
    pass


_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_PROFILE_DIGEST = "406740705e853fa51ad4eacf7a01925fbe4b5cec491be35ea12ba777d217d714"
_SOURCE_LOCK_DIGEST = "14c763218602585d49e12060e1e6cf21d33815fda0cb18711a6522a26157ace2"
_BUILD_PLAN_DIGEST = "809a23879e9e314b835956ef96cec8ede1faaeef1e5c2c06fd7330df600417aa"
_READINESS_DIGEST = "39a3405b4e5da9b79b260f67f9ec975433ed171d8801eb55edc648b1f38370d8"
_EXPECTED_SPECS = {
    "content-cache": ("Shtenco/synergynet", "a8fde01c19420dbe63ca30e1da3b009c0c10064d", "9ce8c608edd65f7c888809c49109fa3a4cecffe58d9434d6c9bf317150e7ee96"),
    "nexus": ("Shtenco/agi_nexus", "cbc06e83f7f9e242719667e446a090894e11eef1", "ab83e935b2cdd2eb855737a18f4e8e039ebb166cfe431d8d1652a44a63af522d"),
    "synergynet": ("Shtenco/synergynet", "a8fde01c19420dbe63ca30e1da3b009c0c10064d", "e74ae38f45d313b301b4f7b4c408485780d1c1f6ebdb68cbd7c0bd3ed13b391c"),
}
_EXPECTED_BLOCKERS = [
    "BUILD_ARTIFACTS_NOT_VERIFIED",
    "BUILD_TOOLCHAIN_NOT_FROZEN",
    "CONTENT_CACHE_SERVICE_INTERFACE_NOT_IMPLEMENTED",
    "NEXUS_SERVICE_INTERFACE_NOT_IMPLEMENTED",
    "SYNERGYNET_SERVICE_INTERFACE_NOT_IMPLEMENTED",
]


def _check(value: Any) -> None:
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int) and not isinstance(value, bool):
        if abs(value) > 2**53 - 1:
            raise NodeReadinessError("unsafe integer")
        return
    if isinstance(value, float):
        raise NodeReadinessError("floating point values are forbidden")
    if isinstance(value, list):
        for item in value:
            _check(item)
        return
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise NodeReadinessError("object keys must be strings")
        for item in value.values():
            _check(item)
        return
    raise NodeReadinessError("unsupported readiness value")


def canonical_json(value: Any) -> bytes:
    _check(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _digest_without(payload: dict[str, Any], field: str) -> str:
    body = dict(payload)
    body.pop(field, None)
    return hashlib.sha256(canonical_json(body)).hexdigest()


def readiness_digest(payload: dict[str, Any]) -> str:
    return _digest_without(payload, "readiness_digest")


def _verify_service_spec(spec: dict[str, Any], service_id: str) -> None:
    if not isinstance(spec, dict) or spec.get("schema") != "synergy.service-spec/v1":
        raise NodeReadinessError("invalid service-spec payload")
    repository, source_commit, digest = _EXPECTED_SPECS[service_id]
    if spec.get("service_id") != service_id or spec.get("repository") != repository or spec.get("source_commit") != source_commit:
        raise NodeReadinessError(f"service-spec source identity mismatch for {service_id}")
    if not _HEX40.fullmatch(source_commit):
        raise NodeReadinessError("invalid source commit")
    if spec.get("spec_digest") != digest or _digest_without(spec, "spec_digest") != digest:
        raise NodeReadinessError(f"service-spec digest mismatch for {service_id}")
    if spec.get("runtime_form") != "PYTHON_LIBRARY_ONLY":
        raise NodeReadinessError("v1 current service generation is library-only")
    for field in ("entrypoint", "health_probe", "lifecycle_protocol", "wire_protocol"):
        if spec.get(field) is not None:
            raise NodeReadinessError(f"v1 service-spec cannot claim {field}")
    if spec.get("readiness_status") != "SERVICE_INTERFACE_NOT_IMPLEMENTED":
        raise NodeReadinessError("service-spec overclaims readiness")
    if spec.get("execution_authority") != "NONE":
        raise NodeReadinessError("service-spec grants execution authority")


@dataclass(frozen=True)
class NodeReadinessDecisionV1:
    status: str
    build_plan_verified: bool
    service_specs_verified: bool
    deployable: bool
    blockers: tuple[str, ...]


def verify_research_node_readiness_v1(
    readiness: dict[str, Any],
    build_plan: dict[str, Any],
    service_specs_by_id: dict[str, dict[str, Any]],
) -> NodeReadinessDecisionV1:
    verify_research_node_build_plan_v1(build_plan)
    if build_plan.get("plan_digest") != _BUILD_PLAN_DIGEST:
        raise NodeReadinessError("wrong build-plan generation")
    if set(service_specs_by_id) != set(_EXPECTED_SPECS):
        raise NodeReadinessError("service-spec set incomplete")
    for service_id in sorted(_EXPECTED_SPECS):
        _verify_service_spec(service_specs_by_id[service_id], service_id)
    required = {
        "schema", "readiness_id", "profile_digest", "source_lock_digest", "build_plan_digest",
        "service_specs", "build_status", "service_status", "node_status", "blockers",
        "execution_authority", "readiness_digest",
    }
    if not isinstance(readiness, dict) or set(readiness) != required:
        raise NodeReadinessError("unexpected readiness shape")
    if readiness["schema"] != "synergy.node-readiness/v1":
        raise NodeReadinessError("unexpected readiness schema")
    if readiness["readiness_id"] != "RESEARCH_COMPUTE_NODE_READINESS_20260822":
        raise NodeReadinessError("unexpected readiness id")
    if readiness["profile_digest"] != _PROFILE_DIGEST or readiness["source_lock_digest"] != _SOURCE_LOCK_DIGEST:
        raise NodeReadinessError("profile/source-lock binding mismatch")
    if readiness["build_plan_digest"] != _BUILD_PLAN_DIGEST:
        raise NodeReadinessError("build-plan binding mismatch")
    expected_refs = []
    for service_id in sorted(_EXPECTED_SPECS):
        repository, source_commit, digest = _EXPECTED_SPECS[service_id]
        expected_refs.append({
            "service_id": service_id,
            "repository": repository,
            "source_commit": source_commit,
            "service_spec_digest": digest,
            "readiness_status": "SERVICE_INTERFACE_NOT_IMPLEMENTED",
        })
    if readiness["service_specs"] != expected_refs:
        raise NodeReadinessError("service-spec references drifted")
    if readiness["build_status"] != "BUILD_PLAN_NOT_REPRODUCIBLE_YET":
        raise NodeReadinessError("readiness overclaims build status")
    if readiness["service_status"] != "SERVICE_INTERFACES_INCOMPLETE":
        raise NodeReadinessError("readiness overclaims service status")
    if readiness["node_status"] != "NODE_NOT_DEPLOYABLE":
        raise NodeReadinessError("readiness overclaims deployability")
    if readiness["blockers"] != _EXPECTED_BLOCKERS:
        raise NodeReadinessError("readiness blockers drifted")
    if readiness["execution_authority"] != "NONE":
        raise NodeReadinessError("readiness artifact grants execution authority")
    supplied = readiness["readiness_digest"]
    if not isinstance(supplied, str) or not _HEX64.fullmatch(supplied):
        raise NodeReadinessError("invalid readiness digest")
    recomputed = readiness_digest(readiness)
    if supplied != recomputed or recomputed != _READINESS_DIGEST:
        raise NodeReadinessError("readiness digest mismatch")
    return NodeReadinessDecisionV1(
        status="NODE_NOT_DEPLOYABLE",
        build_plan_verified=True,
        service_specs_verified=True,
        deployable=False,
        blockers=tuple(_EXPECTED_BLOCKERS),
    )
