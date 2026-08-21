from __future__ import annotations

import hashlib
import json
from typing import Any


class NodeProfileError(ValueError):
    pass


def _canonical(value: Any) -> bytes:
    def check(v: Any) -> None:
        if v is None or isinstance(v, (str, bool)):
            return
        if isinstance(v, int) and not isinstance(v, bool):
            if abs(v) > 2**53 - 1:
                raise NodeProfileError("unsafe integer")
            return
        if isinstance(v, float):
            raise NodeProfileError("floats forbidden in node profile")
        if isinstance(v, list):
            for item in v:
                check(item)
            return
        if isinstance(v, dict):
            if any(not isinstance(k, str) for k in v):
                raise NodeProfileError("profile keys must be strings")
            for item in v.values():
                check(item)
            return
        raise NodeProfileError("unsupported profile value")
    check(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def profile_digest(payload: dict[str, Any]) -> str:
    body = dict(payload)
    body.pop("profile_digest", None)
    return hashlib.sha256(_canonical(body)).hexdigest()


def verify_node_profile(payload: dict[str, Any], *, expected_repositories: set[str]) -> dict[str, Any]:
    expected = {
        "schema", "profile_id", "allowed_capabilities", "required_services",
        "forbidden_service_kinds", "financial_authority", "payment_authority",
        "accounting_authority", "execution_authority", "status", "profile_digest"
    }
    if set(payload) != expected or payload["schema"] != "synergy.node-profile/v1":
        raise NodeProfileError("unexpected node-profile shape/schema")
    if not isinstance(payload["profile_id"], str) or not payload["profile_id"]:
        raise NodeProfileError("profile_id required")
    caps = payload["allowed_capabilities"]
    if not isinstance(caps, list) or not caps or caps != sorted(set(caps)):
        raise NodeProfileError("allowed capabilities must be sorted unique")
    forbidden = payload["forbidden_service_kinds"]
    if not isinstance(forbidden, list) or forbidden != sorted(set(forbidden)):
        raise NodeProfileError("forbidden service kinds must be sorted unique")
    services = payload["required_services"]
    if not isinstance(services, list) or not services:
        raise NodeProfileError("required services are required")
    if services != sorted(services, key=lambda item: item.get("service_id", "")):
        raise NodeProfileError("required services must be sorted by service_id")
    seen: set[str] = set()
    for service in services:
        if not isinstance(service, dict) or set(service) != {"service_id", "kind", "repository", "required_capabilities"}:
            raise NodeProfileError("service profile shape mismatch")
        sid = service["service_id"]
        if not isinstance(sid, str) or not sid or sid in seen:
            raise NodeProfileError("service ids must be unique non-empty")
        seen.add(sid)
        if service["repository"] not in expected_repositories:
            raise NodeProfileError("service repository outside federation")
        required = service["required_capabilities"]
        if not isinstance(required, list) or required != sorted(set(required)) or not set(required).issubset(caps):
            raise NodeProfileError("service capability set invalid")
        if service["kind"] in forbidden:
            raise NodeProfileError("required service kind is also forbidden")
    for field in ("financial_authority", "payment_authority", "accounting_authority", "execution_authority"):
        if payload[field] != "NONE":
            raise NodeProfileError(f"node profile cannot grant {field}")
    if payload["status"] != "ARCHITECTURE_PROFILE_ONLY":
        raise NodeProfileError("unexpected node-profile status")
    if payload["profile_digest"] != profile_digest(payload):
        raise NodeProfileError("node-profile digest mismatch")
    return payload


def verify_research_compute_profile(payload: dict[str, Any], *, expected_repositories: set[str]) -> dict[str, Any]:
    verify_node_profile(payload, expected_repositories=expected_repositories)
    if payload["profile_id"] != "RESEARCH_COMPUTE_NODE":
        raise NodeProfileError("unexpected profile id")
    if payload["allowed_capabilities"] != ["CONTENT_CACHE", "NEXUS_COMPUTE", "P2P_RELAY"]:
        raise NodeProfileError("research node capability profile drifted")
    expected_services = {
        ("content-cache", "CONTENT_CACHE", "Shtenco/synergynet", ("CONTENT_CACHE",)),
        ("nexus", "NEXUS", "Shtenco/agi_nexus", ("NEXUS_COMPUTE",)),
        ("synergynet", "SYNERGYNET", "Shtenco/synergynet", ("P2P_RELAY",)),
    }
    got = {(x["service_id"], x["kind"], x["repository"], tuple(x["required_capabilities"])) for x in payload["required_services"]}
    if got != expected_services:
        raise NodeProfileError("research node service composition drifted")
    required_forbidden = {"AUTOPILOT", "BLOCKCHAIN", "FINANCIAL_OS", "METAPAY"}
    if set(payload["forbidden_service_kinds"]) != required_forbidden:
        raise NodeProfileError("research node forbidden-service boundary drifted")
    return payload
