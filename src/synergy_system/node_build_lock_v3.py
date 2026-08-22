from __future__ import annotations

import hashlib
import json
import re
from typing import Any


class NodeBuildLockV3Error(ValueError):
    pass


HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
PROFILE_DIGEST = "0c9b82e591c5aa30d1f9b499edee02c0b56643af825bbb7eecb93f8651659107"
CAPABILITY_REGISTRY_DIGEST = "3727810480e5660129fc63a2d7999b988ed9ae387365d4501bb50b7ae7257913"
SCIENCE_LOCK_V3_DIGEST = "de35e3f31d85b9ab559180a12535ecdaa58fd70c6d3575d215994064933e1274"

EXPECTED_SERVICES = {
    "content-cache": (
        "CONTENT_CACHE", "Shtenco/synergynet", "874a83b6510420ec43ce99fc4b7936e106ad2339",
        "feat/static-peer-relay-service-v1-20260821", "SYNERGYNET_PERSISTENT_CONTENT_SERVICE_CANDIDATE",
    ),
    "nexus": (
        "NEXUS", "Shtenco/agi_nexus", "2ee8f2a29ad2497afca6c7386375a296cd0bdbcf",
        "feat/smallworld-exact-stdlib-v2-20260822", "NEXUS_SMALLWORLD_EXACT_STDLIB_SERVICE_CANDIDATE",
    ),
    "science-agent": (
        "SCIENCE_AGENT", "Shtenco/nexus_science_agent", "0607690c3036d2fdce2ac3e044094a8e4da0311b",
        "feat/science-service-protocol-v4-20260821", "SCIENCE_AGENT_LOCAL_RESEARCH_SERVICE_CANDIDATE",
    ),
    "synergynet": (
        "SYNERGYNET", "Shtenco/synergynet", "874a83b6510420ec43ce99fc4b7936e106ad2339",
        "feat/static-peer-relay-service-v1-20260821", "SYNERGYNET_STATIC_PEER_RELAY_SERVICE_CANDIDATE",
    ),
}


def canonical_json(value: Any) -> bytes:
    def check(item: Any) -> None:
        if item is None or isinstance(item, (str, bool)):
            return
        if isinstance(item, int) and not isinstance(item, bool):
            if abs(item) > 2**53 - 1:
                raise NodeBuildLockV3Error("unsafe integer")
            return
        if isinstance(item, float):
            raise NodeBuildLockV3Error("floats forbidden in build-lock bytes")
        if isinstance(item, list):
            for child in item:
                check(child)
            return
        if isinstance(item, dict):
            if any(not isinstance(key, str) for key in item):
                raise NodeBuildLockV3Error("object keys must be strings")
            for child in item.values():
                check(child)
            return
        raise NodeBuildLockV3Error(f"unsupported build-lock value: {type(item)!r}")

    check(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def lock_digest(payload: dict[str, Any]) -> str:
    body = dict(payload)
    body.pop("lock_digest", None)
    return hashlib.sha256(canonical_json(body)).hexdigest()


def _hex(value: Any, pattern: re.Pattern[str], label: str) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise NodeBuildLockV3Error(f"invalid {label}")
    return value


def verify_science_source_build_lock_v3(payload: dict[str, Any]) -> dict[str, Any]:
    expected_shape = {
        "schema", "lock_id", "profile_digest", "capability_registry_digest", "services",
        "verification_status", "execution_authority", "lock_digest",
    }
    if not isinstance(payload, dict) or set(payload) != expected_shape:
        raise NodeBuildLockV3Error("unexpected build-lock v3 shape")
    if payload["schema"] != "synergy.node-build-lock/v3":
        raise NodeBuildLockV3Error("unexpected build-lock schema")
    if payload["lock_id"] != "SCIENCE_RESEARCH_NODE_SOURCE_CANDIDATE_20260822":
        raise NodeBuildLockV3Error("unexpected build-lock generation")
    if payload["profile_digest"] != PROFILE_DIGEST:
        raise NodeBuildLockV3Error("profile digest drift")
    if payload["capability_registry_digest"] != CAPABILITY_REGISTRY_DIGEST:
        raise NodeBuildLockV3Error("capability registry digest drift")
    _hex(payload["profile_digest"], HEX64, "profile digest")
    _hex(payload["capability_registry_digest"], HEX64, "capability registry digest")
    _hex(payload["lock_digest"], HEX64, "lock digest")

    services = payload["services"]
    if not isinstance(services, list) or services != sorted(services, key=lambda item: item.get("service_id", "")):
        raise NodeBuildLockV3Error("services must be sorted by service_id")
    if len(services) != len(EXPECTED_SERVICES):
        raise NodeBuildLockV3Error("Science Node service count drift")

    seen: set[str] = set()
    for service in services:
        expected_fields = {
            "service_id", "kind", "repository", "source_commit", "source_ref", "source_role",
            "build_artifact_digest", "build_evidence_digest", "build_status",
        }
        if not isinstance(service, dict) or set(service) != expected_fields:
            raise NodeBuildLockV3Error("unexpected service shape")
        service_id = service["service_id"]
        if not isinstance(service_id, str) or service_id in seen or service_id not in EXPECTED_SERVICES:
            raise NodeBuildLockV3Error("unexpected or duplicate service id")
        seen.add(service_id)
        expected = EXPECTED_SERVICES[service_id]
        actual = (
            service["kind"], service["repository"], service["source_commit"], service["source_ref"],
            service["source_role"],
        )
        if actual != expected:
            raise NodeBuildLockV3Error(f"source identity drift for {service_id}")
        _hex(service["source_commit"], HEX40, "source commit")
        if service["build_artifact_digest"] is not None or service["build_evidence_digest"] is not None:
            raise NodeBuildLockV3Error("v3 source lock cannot claim build artifact/evidence")
        if service["build_status"] != "SOURCE_CANDIDATE_NOT_BUILD_VERIFIED":
            raise NodeBuildLockV3Error("v3 source lock cannot claim build verification")

    if seen != set(EXPECTED_SERVICES):
        raise NodeBuildLockV3Error("Science Node service coverage incomplete")
    if payload["verification_status"] != "SOURCE_IDENTITY_FROZEN_BUILD_NOT_VERIFIED":
        raise NodeBuildLockV3Error("v3 source lock overclaims build status")
    if payload["execution_authority"] != "NONE":
        raise NodeBuildLockV3Error("source lock cannot execute services")
    calculated = lock_digest(payload)
    if calculated != payload["lock_digest"] or calculated != SCIENCE_LOCK_V3_DIGEST:
        raise NodeBuildLockV3Error("canonical Science Node build-lock v3 digest mismatch")
    canonical_json(payload)
    return payload
