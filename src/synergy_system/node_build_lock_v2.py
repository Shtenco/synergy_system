from __future__ import annotations

import hashlib
import json
import re
from typing import Any


class NodeBuildLockV2Error(ValueError):
    pass


_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_PROFILE_DIGEST = "406740705e853fa51ad4eacf7a01925fbe4b5cec491be35ea12ba777d217d714"
_SUPERSEDES = "14c763218602585d49e12060e1e6cf21d33815fda0cb18711a6522a26157ace2"
_LOCK_DIGEST = "14aa9c6e1ce246a740fe36ea514b2abc704f4f26dc9b9e797bab1b263e4a3666"
_EXPECTED = {
    "content-cache": {
        "kind": "CONTENT_CACHE",
        "repository": "Shtenco/synergynet",
        "source_commit": "0aa548ee8f1b4dc7046cefa5694f9b496d312145",
        "source_ref": "feat/persistent-content-service-v1-20260821",
        "service_descriptor_path": "config/persistent_content_service_v2.json",
        "service_descriptor_digest": "648f0b8bcbcff244e7dfd2e5d4d660e48a6c30dbbe9310e8f45b72dd73e35c63",
        "required_capabilities": ["CONTENT_CACHE"],
    },
    "nexus": {
        "kind": "NEXUS",
        "repository": "Shtenco/agi_nexus",
        "source_commit": "ef1a6e3675e53fda4bf91566aec61f1b62fa9336",
        "source_ref": "feat/smallworld-service-protocol-v1-20260821",
        "service_descriptor_path": "config/smallworld_compute_service_v1.json",
        "service_descriptor_digest": "69806f75f21bb34f818a3455c61269685d11922d5540e27752df7360ebff2a2d",
        "required_capabilities": ["NEXUS_COMPUTE"],
    },
    "synergynet": {
        "kind": "SYNERGYNET",
        "repository": "Shtenco/synergynet",
        "source_commit": "874a83b6510420ec43ce99fc4b7936e106ad2339",
        "source_ref": "feat/static-peer-relay-service-v1-20260821",
        "service_descriptor_path": "config/static_peer_relay_service_v1.json",
        "service_descriptor_digest": "0e4fe4aed2d4eb1339e930ccb7c7ce2d574acdd94c0759dbefd2167e61659e18",
        "required_capabilities": ["P2P_RELAY"],
    },
}


def _canonical(value: Any) -> bytes:
    def check(item: Any) -> None:
        if item is None or isinstance(item, (str, bool)):
            return
        if isinstance(item, int) and not isinstance(item, bool):
            if abs(item) > 2**53 - 1:
                raise NodeBuildLockV2Error("unsafe integer")
            return
        if isinstance(item, float):
            raise NodeBuildLockV2Error("floats forbidden in node build lock")
        if isinstance(item, list):
            for child in item:
                check(child)
            return
        if isinstance(item, dict):
            if any(not isinstance(key, str) for key in item):
                raise NodeBuildLockV2Error("object keys must be strings")
            for child in item.values():
                check(child)
            return
        raise NodeBuildLockV2Error("unsupported node build lock value")

    check(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def lock_digest(payload: dict[str, Any]) -> str:
    body = dict(payload)
    body.pop("lock_digest", None)
    return hashlib.sha256(_canonical(body)).hexdigest()


def service_descriptor_digest(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def _validate_descriptor(service_id: str, descriptor: dict[str, Any], expected: dict[str, Any]) -> None:
    if service_descriptor_digest(descriptor) != expected["service_descriptor_digest"]:
        raise NodeBuildLockV2Error(f"service descriptor bytes drifted for {service_id}")
    if descriptor.get("service_kind") != expected["kind"]:
        raise NodeBuildLockV2Error(f"descriptor kind drifted for {service_id}")
    if descriptor.get("required_capabilities") != expected["required_capabilities"]:
        raise NodeBuildLockV2Error(f"descriptor capabilities drifted for {service_id}")
    if descriptor.get("build_artifact_digest") is not None:
        raise NodeBuildLockV2Error(f"source-candidate descriptor overclaims build artifact for {service_id}")
    if descriptor.get("build_status") != "SERVICE_SOURCE_CANDIDATE_NOT_BUILD_VERIFIED":
        raise NodeBuildLockV2Error(f"unexpected descriptor build status for {service_id}")
    if descriptor.get("execution_authority") != "NONE":
        raise NodeBuildLockV2Error(f"service descriptor cannot grant execution authority for {service_id}")


def verify_research_service_build_lock_v2(
    payload: dict[str, Any],
    *,
    profile: dict[str, Any] | None = None,
    descriptors: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    expected_fields = {
        "schema", "lock_id", "profile_digest", "supersedes_lock_digest", "services",
        "verification_status", "financial_authority", "payment_authority", "accounting_authority",
        "execution_authority", "lock_digest"
    }
    if not isinstance(payload, dict) or set(payload) != expected_fields:
        raise NodeBuildLockV2Error("unexpected node-build-lock v2 shape")
    if payload["schema"] != "synergy.node-build-lock/v2":
        raise NodeBuildLockV2Error("unexpected node-build-lock schema")
    if payload["lock_id"] != "RESEARCH_COMPUTE_NODE_SERVICE_CANDIDATE_20260821":
        raise NodeBuildLockV2Error("unexpected research service lock id")
    if payload["profile_digest"] != _PROFILE_DIGEST:
        raise NodeBuildLockV2Error("service lock bound to wrong node profile")
    if payload["supersedes_lock_digest"] != _SUPERSEDES:
        raise NodeBuildLockV2Error("service lock does not supersede expected source lock")

    services = payload["services"]
    if not isinstance(services, list) or services != sorted(services, key=lambda item: item.get("service_id", "")):
        raise NodeBuildLockV2Error("services must be sorted by service_id")
    if len(services) != len(_EXPECTED):
        raise NodeBuildLockV2Error("service set drifted")

    profile_services: dict[str, dict[str, Any]] = {}
    if profile is not None:
        if profile.get("profile_digest") != _PROFILE_DIGEST or profile.get("profile_id") != "RESEARCH_COMPUTE_NODE":
            raise NodeBuildLockV2Error("wrong architecture profile supplied")
        required_services = profile.get("required_services")
        if not isinstance(required_services, list):
            raise NodeBuildLockV2Error("profile required_services missing")
        profile_services = {item.get("service_id"): item for item in required_services if isinstance(item, dict)}
        if set(profile_services) != set(_EXPECTED):
            raise NodeBuildLockV2Error("profile service set does not match service lock")

    seen: set[str] = set()
    for service in services:
        expected_service_fields = {
            "service_id", "kind", "repository", "source_commit", "source_ref",
            "service_descriptor_path", "service_descriptor_digest", "required_capabilities",
            "service_source_status", "build_artifact_digest", "build_status"
        }
        if not isinstance(service, dict) or set(service) != expected_service_fields:
            raise NodeBuildLockV2Error("unexpected service-lock entry shape")
        service_id = service["service_id"]
        if service_id in seen or service_id not in _EXPECTED:
            raise NodeBuildLockV2Error("unexpected or duplicate service id")
        seen.add(service_id)
        expected = _EXPECTED[service_id]
        for field in (
            "kind", "repository", "source_commit", "source_ref", "service_descriptor_path",
            "service_descriptor_digest", "required_capabilities"
        ):
            if service[field] != expected[field]:
                raise NodeBuildLockV2Error(f"service identity drifted for {service_id}:{field}")
        if not _HEX40.fullmatch(service["source_commit"]):
            raise NodeBuildLockV2Error("source commit must be lowercase git sha")
        if not _HEX64.fullmatch(service["service_descriptor_digest"]):
            raise NodeBuildLockV2Error("service descriptor digest must be lowercase sha256")
        if service["service_source_status"] != "SERVICE_SOURCE_CANDIDATE_NOT_BUILD_VERIFIED":
            raise NodeBuildLockV2Error("service source status overclaims evidence")
        if service["build_artifact_digest"] is not None or service["build_status"] != "BUILD_ARTIFACT_MISSING":
            raise NodeBuildLockV2Error("v2 service lock cannot claim build evidence")

        if profile is not None:
            p = profile_services[service_id]
            if p.get("kind") != service["kind"] or p.get("repository") != service["repository"]:
                raise NodeBuildLockV2Error(f"service does not match architecture profile for {service_id}")
            if p.get("required_capabilities") != service["required_capabilities"]:
                raise NodeBuildLockV2Error(f"capabilities do not match architecture profile for {service_id}")

        if descriptors is not None:
            if service_id not in descriptors:
                raise NodeBuildLockV2Error(f"descriptor missing for {service_id}")
            _validate_descriptor(service_id, descriptors[service_id], expected)

    if seen != set(_EXPECTED):
        raise NodeBuildLockV2Error("service set incomplete")
    if payload["verification_status"] != "SERVICE_SOURCE_GRAPH_FROZEN_BUILD_NOT_VERIFIED":
        raise NodeBuildLockV2Error("verification status overclaims evidence")
    for authority in ("financial_authority", "payment_authority", "accounting_authority", "execution_authority"):
        if payload[authority] != "NONE":
            raise NodeBuildLockV2Error(f"service lock cannot grant {authority}")
    supplied = payload["lock_digest"]
    if not isinstance(supplied, str) or not _HEX64.fullmatch(supplied):
        raise NodeBuildLockV2Error("lock digest must be lowercase sha256")
    recomputed = lock_digest(payload)
    if supplied != recomputed or recomputed != _LOCK_DIGEST:
        raise NodeBuildLockV2Error("research service build lock digest mismatch")
    return payload
