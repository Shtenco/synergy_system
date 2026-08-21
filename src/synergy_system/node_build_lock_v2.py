from __future__ import annotations

import hashlib
import json
import re
from typing import Any


class NodeBuildLockV2Error(ValueError):
    pass


HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
PROFILE_DIGEST = "0c9b82e591c5aa30d1f9b499edee02c0b56643af825bbb7eecb93f8651659107"
REGISTRY_DIGEST = "3727810480e5660129fc63a2d7999b988ed9ae387365d4501bb50b7ae7257913"
SCIENCE_LOCK_DIGEST = "24e4a3c6ed23c2e156b07821fb3b1e0e232651c256bc3b750d2ed25bee477757"

EXPECTED_SCIENCE_SERVICES = {
    "content-cache": ("CONTENT_CACHE", "Shtenco/synergynet", "874a83b6510420ec43ce99fc4b7936e106ad2339", "feat/static-peer-relay-service-v1-20260821", "SYNERGYNET_PERSISTENT_CONTENT_SERVICE_CANDIDATE"),
    "nexus": ("NEXUS", "Shtenco/agi_nexus", "ef1a6e3675e53fda4bf91566aec61f1b62fa9336", "feat/smallworld-service-protocol-v1-20260821", "NEXUS_SMALLWORLD_SERVICE_CANDIDATE"),
    "science-agent": ("SCIENCE_AGENT", "Shtenco/nexus_science_agent", "0607690c3036d2fdce2ac3e044094a8e4da0311b", "feat/science-service-protocol-v4-20260821", "SCIENCE_AGENT_LOCAL_RESEARCH_SERVICE_CANDIDATE"),
    "synergynet": ("SYNERGYNET", "Shtenco/synergynet", "874a83b6510420ec43ce99fc4b7936e106ad2339", "feat/static-peer-relay-service-v1-20260821", "SYNERGYNET_STATIC_PEER_RELAY_SERVICE_CANDIDATE"),
}


def canonical_json(value: Any) -> bytes:
    def check(v: Any) -> None:
        if v is None or isinstance(v, (str, bool)):
            return
        if isinstance(v, int) and not isinstance(v, bool):
            if abs(v) > 2**53 - 1:
                raise NodeBuildLockV2Error("unsafe integer")
            return
        if isinstance(v, float):
            raise NodeBuildLockV2Error("floats forbidden in build lock")
        if isinstance(v, list):
            for item in v:
                check(item)
            return
        if isinstance(v, dict):
            if any(not isinstance(k, str) for k in v):
                raise NodeBuildLockV2Error("object keys must be strings")
            for item in v.values():
                check(item)
            return
        raise NodeBuildLockV2Error("unsupported build-lock value")
    check(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def lock_digest(payload: dict[str, Any]) -> str:
    body = dict(payload)
    body.pop("lock_digest", None)
    return hashlib.sha256(canonical_json(body)).hexdigest()


def verify_node_build_lock_v2(payload: dict[str, Any]) -> dict[str, Any]:
    expected = {"schema", "lock_id", "profile_digest", "capability_registry_digest", "services", "verification_status", "execution_authority", "lock_digest"}
    if not isinstance(payload, dict) or set(payload) != expected:
        raise NodeBuildLockV2Error("unexpected build-lock v2 shape")
    if payload["schema"] != "synergy.node-build-lock/v2":
        raise NodeBuildLockV2Error("unexpected build-lock schema")
    for field in ("profile_digest", "capability_registry_digest", "lock_digest"):
        if not isinstance(payload[field], str) or not HEX64.fullmatch(payload[field]):
            raise NodeBuildLockV2Error(f"{field} must be lowercase sha256")
    if not isinstance(payload["lock_id"], str) or not payload["lock_id"]:
        raise NodeBuildLockV2Error("lock_id required")
    services = payload["services"]
    if not isinstance(services, list) or not services or services != sorted(services, key=lambda x:x.get("service_id", "")):
        raise NodeBuildLockV2Error("services must be non-empty and sorted by service_id")
    seen: set[str] = set()
    statuses: list[str] = []
    for service in services:
        fields = {"service_id", "kind", "repository", "source_commit", "source_ref", "source_role", "build_artifact_digest", "build_evidence_digest", "build_status"}
        if not isinstance(service, dict) or set(service) != fields:
            raise NodeBuildLockV2Error("unexpected build-lock service shape")
        sid = service["service_id"]
        if not isinstance(sid, str) or not sid or sid in seen:
            raise NodeBuildLockV2Error("service_id must be unique and non-empty")
        seen.add(sid)
        if not isinstance(service["kind"], str) or service["kind"] != service["kind"].upper():
            raise NodeBuildLockV2Error("service kind invalid")
        if not isinstance(service["repository"], str) or not service["repository"].startswith("Shtenco/"):
            raise NodeBuildLockV2Error("service repository invalid")
        if not isinstance(service["source_commit"], str) or not HEX40.fullmatch(service["source_commit"]):
            raise NodeBuildLockV2Error("source commit must be lowercase git sha")
        if not isinstance(service["source_ref"], str) or not service["source_ref"]:
            raise NodeBuildLockV2Error("source_ref required")
        if not isinstance(service["source_role"], str) or not service["source_role"] or service["source_role"] != service["source_role"].upper():
            raise NodeBuildLockV2Error("source_role must be uppercase")
        status = service["build_status"]
        statuses.append(status)
        artifact = service["build_artifact_digest"]
        evidence = service["build_evidence_digest"]
        if status == "SOURCE_CANDIDATE_NOT_BUILD_VERIFIED":
            if artifact is not None or evidence is not None:
                raise NodeBuildLockV2Error("source-only candidate cannot claim build/evidence digest")
        elif status == "BUILD_ARTIFACT_FROZEN_TESTS_PENDING":
            if not isinstance(artifact, str) or not HEX64.fullmatch(artifact) or evidence is not None:
                raise NodeBuildLockV2Error("artifact-frozen status requires artifact digest and no test evidence")
        elif status == "BUILD_VERIFIED":
            if not isinstance(artifact, str) or not HEX64.fullmatch(artifact) or not isinstance(evidence, str) or not HEX64.fullmatch(evidence):
                raise NodeBuildLockV2Error("build-verified status requires artifact and evidence digests")
        else:
            raise NodeBuildLockV2Error("unknown build status")
    if all(s == "SOURCE_CANDIDATE_NOT_BUILD_VERIFIED" for s in statuses):
        expected_status = "SOURCE_IDENTITY_FROZEN_BUILD_NOT_VERIFIED"
    elif all(s == "BUILD_VERIFIED" for s in statuses):
        expected_status = "BUILD_VERIFIED"
    else:
        expected_status = "BUILD_EVIDENCE_INCOMPLETE"
    if payload["verification_status"] != expected_status:
        raise NodeBuildLockV2Error("overall build verification status inconsistent with services")
    if payload["execution_authority"] != "NONE":
        raise NodeBuildLockV2Error("build lock does not execute services")
    if payload["lock_digest"] != lock_digest(payload):
        raise NodeBuildLockV2Error("build-lock digest mismatch")
    return payload


def verify_science_source_build_lock_v2(payload: dict[str, Any]) -> dict[str, Any]:
    verify_node_build_lock_v2(payload)
    if payload["lock_id"] != "SCIENCE_RESEARCH_NODE_SOURCE_CANDIDATE_20260821":
        raise NodeBuildLockV2Error("unexpected science lock id")
    if payload["profile_digest"] != PROFILE_DIGEST or payload["capability_registry_digest"] != REGISTRY_DIGEST:
        raise NodeBuildLockV2Error("science lock bound to wrong profile or capability registry")
    if payload["lock_digest"] != SCIENCE_LOCK_DIGEST:
        raise NodeBuildLockV2Error("science build-lock digest drifted")
    if len(payload["services"]) != len(EXPECTED_SCIENCE_SERVICES):
        raise NodeBuildLockV2Error("science build-lock service set drifted")
    seen: set[str] = set()
    for service in payload["services"]:
        sid = service["service_id"]
        if sid not in EXPECTED_SCIENCE_SERVICES or sid in seen:
            raise NodeBuildLockV2Error("unexpected science service")
        seen.add(sid)
        expected = EXPECTED_SCIENCE_SERVICES[sid]
        got = (service["kind"], service["repository"], service["source_commit"], service["source_ref"], service["source_role"])
        if got != expected:
            raise NodeBuildLockV2Error(f"science source identity drifted for {sid}")
        if service["build_status"] != "SOURCE_CANDIDATE_NOT_BUILD_VERIFIED":
            raise NodeBuildLockV2Error("science v2 fixture cannot overclaim build verification")
    if seen != set(EXPECTED_SCIENCE_SERVICES):
        raise NodeBuildLockV2Error("science build-lock service set incomplete")
    return payload
