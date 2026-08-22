from __future__ import annotations

import hashlib
import json
import re
from typing import Any


class NodeBuildPlanError(ValueError):
    pass


_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_PROFILE_DIGEST = "406740705e853fa51ad4eacf7a01925fbe4b5cec491be35ea12ba777d217d714"
_SOURCE_LOCK_DIGEST = "14c763218602585d49e12060e1e6cf21d33815fda0cb18711a6522a26157ace2"
_PLAN_DIGEST = "809a23879e9e314b835956ef96cec8ede1faaeef1e5c2c06fd7330df600417aa"
_EXPECTED = {
    "content-cache": (
        "Shtenco/synergynet",
        "a8fde01c19420dbe63ca30e1da3b009c0c10064d",
        "1e885eefc5b244efb8e0b0031c88fbb85788677d655f3a595fa9a29b1645029a",
    ),
    "nexus": (
        "Shtenco/agi_nexus",
        "cbc06e83f7f9e242719667e446a090894e11eef1",
        "b262c98666843da80f37bcfae4d8b2105aa3b52b758a3a50406b198afc1a15be",
    ),
    "synergynet": (
        "Shtenco/synergynet",
        "a8fde01c19420dbe63ca30e1da3b009c0c10064d",
        "1e885eefc5b244efb8e0b0031c88fbb85788677d655f3a595fa9a29b1645029a",
    ),
}


def _canonical(value: Any) -> bytes:
    def check(item: Any) -> None:
        if item is None or isinstance(item, (str, bool)):
            return
        if isinstance(item, int) and not isinstance(item, bool):
            if abs(item) > 2**53 - 1:
                raise NodeBuildPlanError("unsafe integer")
            return
        if isinstance(item, float):
            raise NodeBuildPlanError("floating point values are forbidden")
        if isinstance(item, list):
            for child in item:
                check(child)
            return
        if isinstance(item, dict):
            if any(not isinstance(key, str) for key in item):
                raise NodeBuildPlanError("object keys must be strings")
            for child in item.values():
                check(child)
            return
        raise NodeBuildPlanError("unsupported build-plan value")

    check(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def plan_digest(payload: dict[str, Any]) -> str:
    body = dict(payload)
    body.pop("plan_digest", None)
    return hashlib.sha256(_canonical(body)).hexdigest()


def verify_research_node_build_plan_v1(payload: dict[str, Any]) -> dict[str, Any]:
    required = {
        "schema", "plan_id", "profile_digest", "source_lock_digest", "services",
        "plan_status", "execution_authority", "plan_digest",
    }
    if not isinstance(payload, dict) or set(payload) != required:
        raise NodeBuildPlanError("unexpected node build-plan shape")
    if payload["schema"] != "synergy.node-build-plan/v1":
        raise NodeBuildPlanError("unexpected node build-plan schema")
    if payload["plan_id"] != "RESEARCH_COMPUTE_NODE_BUILD_PLAN_SOURCE_CANDIDATE_20260822":
        raise NodeBuildPlanError("unexpected build plan id")
    if payload["profile_digest"] != _PROFILE_DIGEST:
        raise NodeBuildPlanError("build plan bound to wrong node profile")
    if payload["source_lock_digest"] != _SOURCE_LOCK_DIGEST:
        raise NodeBuildPlanError("build plan bound to wrong source lock")
    services = payload["services"]
    if not isinstance(services, list) or services != sorted(services, key=lambda item: item.get("service_id", "")):
        raise NodeBuildPlanError("services must be sorted by service_id")
    if len(services) != len(_EXPECTED):
        raise NodeBuildPlanError("service set drifted")
    seen: set[str] = set()
    for service in services:
        fields = {
            "service_id", "repository", "source_commit", "build_recipe_digest",
            "build_artifact_digest", "reproducibility_status",
        }
        if not isinstance(service, dict) or set(service) != fields:
            raise NodeBuildPlanError("unexpected build-plan service shape")
        sid = service["service_id"]
        if sid in seen or sid not in _EXPECTED:
            raise NodeBuildPlanError("unexpected or duplicate service")
        seen.add(sid)
        repository, source_commit, recipe_digest_expected = _EXPECTED[sid]
        if service["repository"] != repository:
            raise NodeBuildPlanError(f"repository drifted for {sid}")
        if service["source_commit"] != source_commit or not _HEX40.fullmatch(service["source_commit"]):
            raise NodeBuildPlanError(f"source commit drifted for {sid}")
        if service["build_recipe_digest"] != recipe_digest_expected or not _HEX64.fullmatch(service["build_recipe_digest"]):
            raise NodeBuildPlanError(f"build recipe digest drifted for {sid}")
        if service["build_artifact_digest"] is not None:
            raise NodeBuildPlanError("v1 build plan cannot claim built artifact digests")
        if service["reproducibility_status"] != "NOT_REPRODUCIBLE_TOOLCHAIN_NOT_FROZEN":
            raise NodeBuildPlanError("v1 service cannot claim reproducible build status")
    if seen != set(_EXPECTED):
        raise NodeBuildPlanError("service set incomplete")
    if payload["plan_status"] != "BUILD_PLAN_NOT_REPRODUCIBLE_YET":
        raise NodeBuildPlanError("v1 build plan overclaims readiness")
    if payload["execution_authority"] != "NONE":
        raise NodeBuildPlanError("build plan cannot grant execution authority")
    supplied = payload["plan_digest"]
    if not isinstance(supplied, str) or not _HEX64.fullmatch(supplied):
        raise NodeBuildPlanError("invalid plan digest")
    recomputed = plan_digest(payload)
    if supplied != recomputed or recomputed != _PLAN_DIGEST:
        raise NodeBuildPlanError("research node build-plan digest mismatch")
    return payload
