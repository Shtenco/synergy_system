from __future__ import annotations

import hashlib
import json
import re
from typing import Any


class NodeBuildLockError(ValueError):
    pass


_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_PROFILE_DIGEST = "406740705e853fa51ad4eacf7a01925fbe4b5cec491be35ea12ba777d217d714"
_LOCK_DIGEST = "14c763218602585d49e12060e1e6cf21d33815fda0cb18711a6522a26157ace2"
_EXPECTED = {
    "content-cache": {
        "repository": "Shtenco/synergynet",
        "source_commit": "a8fde01c19420dbe63ca30e1da3b009c0c10064d",
        "source_ref": "feat/persistent-store-codec-v3-20260821",
        "source_role": "SYNERGYNET_PERSISTENT_CACHE_CANDIDATE",
    },
    "nexus": {
        "repository": "Shtenco/agi_nexus",
        "source_commit": "cbc06e83f7f9e242719667e446a090894e11eef1",
        "source_ref": "feat/smallworld-kernel-migration-v1-20260821",
        "source_role": "NEXUS_SMALLWORLD_KERNEL_CANDIDATE",
    },
    "synergynet": {
        "repository": "Shtenco/synergynet",
        "source_commit": "a8fde01c19420dbe63ca30e1da3b009c0c10064d",
        "source_ref": "feat/persistent-store-codec-v3-20260821",
        "source_role": "SYNERGYNET_TRANSPORT_CANDIDATE",
    },
}


def _canonical(value: Any) -> bytes:
    def check(item: Any) -> None:
        if item is None or isinstance(item, (str, bool)):
            return
        if isinstance(item, int) and not isinstance(item, bool):
            if abs(item) > 2**53 - 1:
                raise NodeBuildLockError("unsafe integer")
            return
        if isinstance(item, float):
            raise NodeBuildLockError("floats forbidden in node build lock")
        if isinstance(item, list):
            for child in item:
                check(child)
            return
        if isinstance(item, dict):
            if any(not isinstance(key, str) for key in item):
                raise NodeBuildLockError("object keys must be strings")
            for child in item.values():
                check(child)
            return
        raise NodeBuildLockError("unsupported node build lock value")

    check(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def lock_digest(payload: dict[str, Any]) -> str:
    body = dict(payload)
    body.pop("lock_digest", None)
    return hashlib.sha256(_canonical(body)).hexdigest()


def verify_research_source_build_lock(payload: dict[str, Any]) -> dict[str, Any]:
    expected_fields = {
        "schema", "lock_id", "profile_digest", "services", "verification_status",
        "execution_authority", "lock_digest"
    }
    if not isinstance(payload, dict) or set(payload) != expected_fields:
        raise NodeBuildLockError("unexpected node-build-lock shape")
    if payload["schema"] != "synergy.node-build-lock/v1":
        raise NodeBuildLockError("unexpected node-build-lock schema")
    if payload["lock_id"] != "RESEARCH_COMPUTE_NODE_SOURCE_CANDIDATE_20260821":
        raise NodeBuildLockError("unexpected research build lock id")
    if payload["profile_digest"] != _PROFILE_DIGEST:
        raise NodeBuildLockError("build lock bound to wrong node profile")
    services = payload["services"]
    if not isinstance(services, list) or services != sorted(services, key=lambda item: item.get("service_id", "")):
        raise NodeBuildLockError("services must be sorted by service_id")
    if len(services) != len(_EXPECTED):
        raise NodeBuildLockError("research build lock service set drifted")
    seen: set[str] = set()
    for service in services:
        expected_service_fields = {
            "service_id", "repository", "source_commit", "source_ref", "source_role",
            "build_artifact_digest", "build_status"
        }
        if not isinstance(service, dict) or set(service) != expected_service_fields:
            raise NodeBuildLockError("unexpected build-lock service shape")
        sid = service["service_id"]
        if sid in seen or sid not in _EXPECTED:
            raise NodeBuildLockError("unexpected or duplicate service id")
        seen.add(sid)
        expected = _EXPECTED[sid]
        for field in ("repository", "source_commit", "source_ref", "source_role"):
            if service[field] != expected[field]:
                raise NodeBuildLockError(f"source identity drifted for {sid}:{field}")
        if not _HEX40.fullmatch(service["source_commit"]):
            raise NodeBuildLockError("source commit must be lowercase git sha")
        # This generation freezes source only. It must not pretend a build happened.
        if service["build_artifact_digest"] is not None:
            raise NodeBuildLockError("v1 source lock cannot claim a built artifact digest")
        if service["build_status"] != "SOURCE_CANDIDATE_NOT_BUILD_VERIFIED":
            raise NodeBuildLockError("unexpected source build status")
    if seen != set(_EXPECTED):
        raise NodeBuildLockError("research build lock service set incomplete")
    if payload["verification_status"] != "SOURCE_IDENTITY_FROZEN_BUILD_NOT_VERIFIED":
        raise NodeBuildLockError("build verification status overclaims evidence")
    if payload["execution_authority"] != "NONE":
        raise NodeBuildLockError("source build lock cannot execute services")
    supplied = payload["lock_digest"]
    if not isinstance(supplied, str) or not _HEX64.fullmatch(supplied):
        raise NodeBuildLockError("lock digest must be lowercase sha256")
    recomputed = lock_digest(payload)
    if supplied != recomputed or recomputed != _LOCK_DIGEST:
        raise NodeBuildLockError("research source build lock digest mismatch")
    return payload
