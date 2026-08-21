from __future__ import annotations

from typing import Any

from .node_profile_v1 import NodeProfileError, verify_node_profile


EXPECTED_CAPABILITIES = ["CONTENT_CACHE", "NEXUS_COMPUTE", "P2P_RELAY", "SCIENCE_RESEARCH"]
EXPECTED_FORBIDDEN = {"AUTOPILOT", "BLOCKCHAIN", "FINANCIAL_OS", "METAPAY", "MIDAS"}
EXPECTED_SERVICES = {
    ("content-cache", "CONTENT_CACHE", "Shtenco/synergynet", ("CONTENT_CACHE",)),
    ("nexus", "NEXUS", "Shtenco/agi_nexus", ("NEXUS_COMPUTE",)),
    ("science-agent", "SCIENCE_AGENT", "Shtenco/nexus_science_agent", ("SCIENCE_RESEARCH",)),
    ("synergynet", "SYNERGYNET", "Shtenco/synergynet", ("P2P_RELAY",)),
}


def verify_science_research_profile(payload: dict[str, Any], *, expected_repositories: set[str]) -> dict[str, Any]:
    verify_node_profile(payload, expected_repositories=expected_repositories)
    if payload["profile_id"] != "SCIENCE_RESEARCH_NODE":
        raise NodeProfileError("unexpected science profile id")
    if payload["allowed_capabilities"] != EXPECTED_CAPABILITIES:
        raise NodeProfileError("science node capability profile drifted")
    got = {(x["service_id"], x["kind"], x["repository"], tuple(x["required_capabilities"])) for x in payload["required_services"]}
    if got != EXPECTED_SERVICES:
        raise NodeProfileError("science node service composition drifted")
    if set(payload["forbidden_service_kinds"]) != EXPECTED_FORBIDDEN:
        raise NodeProfileError("science node forbidden-service boundary drifted")
    return payload
