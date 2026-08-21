from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from synergy_system.node_build_lock_v2 import (
    NodeBuildLockV2Error,
    lock_digest,
    verify_research_service_build_lock_v2,
)


ROOT = Path(__file__).resolve().parents[1]


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text())


def _evidence() -> tuple[dict, dict, dict[str, dict]]:
    lock = _load("fixtures/node_build_locks/research_compute_node_service_candidate_v2.json")
    profile = _load("fixtures/node_profiles/research_compute_node_v1.json")
    descriptors = {
        "content-cache": _load("fixtures/service_descriptors/synergynet_content_cache_service_v2.json"),
        "nexus": _load("fixtures/service_descriptors/nexus_smallworld_service_v1.json"),
        "synergynet": _load("fixtures/service_descriptors/synergynet_static_relay_service_v1.json"),
    }
    return lock, profile, descriptors


def test_canonical_service_source_lock_verifies_against_profile_and_exact_descriptors() -> None:
    lock, profile, descriptors = _evidence()
    assert verify_research_service_build_lock_v2(lock, profile=profile, descriptors=descriptors) == lock
    assert lock["verification_status"] == "SERVICE_SOURCE_GRAPH_FROZEN_BUILD_NOT_VERIFIED"
    assert all(item["build_artifact_digest"] is None for item in lock["services"])


def test_descriptor_semantic_drift_is_rejected_even_if_descriptor_is_self_consistent() -> None:
    lock, profile, descriptors = _evidence()
    descriptors["content-cache"] = deepcopy(descriptors["content-cache"])
    descriptors["content-cache"]["required_capabilities"] = ["CONTENT_CACHE", "P2P_RELAY"]
    with pytest.raises(NodeBuildLockV2Error, match="descriptor bytes drifted|descriptor capabilities drifted"):
        verify_research_service_build_lock_v2(lock, profile=profile, descriptors=descriptors)


def test_source_commit_tamper_with_fresh_outer_hash_still_fails() -> None:
    lock, profile, descriptors = _evidence()
    tampered = deepcopy(lock)
    tampered["services"][1]["source_commit"] = "0" * 40
    tampered["lock_digest"] = lock_digest(tampered)
    with pytest.raises(NodeBuildLockV2Error, match="source_commit"):
        verify_research_service_build_lock_v2(tampered, profile=profile, descriptors=descriptors)


def test_fake_build_evidence_with_fresh_hash_is_rejected() -> None:
    lock, profile, descriptors = _evidence()
    tampered = deepcopy(lock)
    tampered["services"][0]["build_artifact_digest"] = "1" * 64
    tampered["services"][0]["build_status"] = "BUILD_VERIFIED"
    tampered["lock_digest"] = lock_digest(tampered)
    with pytest.raises(NodeBuildLockV2Error, match="cannot claim build evidence"):
        verify_research_service_build_lock_v2(tampered, profile=profile, descriptors=descriptors)


def test_profile_service_mismatch_is_rejected() -> None:
    lock, profile, descriptors = _evidence()
    bad_profile = deepcopy(profile)
    bad_profile["required_services"][0]["repository"] = "Shtenco/other"
    with pytest.raises(NodeBuildLockV2Error, match="architecture profile"):
        verify_research_service_build_lock_v2(lock, profile=bad_profile, descriptors=descriptors)


def test_authority_escalation_with_fresh_hash_is_rejected() -> None:
    lock, profile, descriptors = _evidence()
    tampered = deepcopy(lock)
    tampered["execution_authority"] = "DEPLOY"
    tampered["lock_digest"] = lock_digest(tampered)
    with pytest.raises(NodeBuildLockV2Error, match="execution_authority"):
        verify_research_service_build_lock_v2(tampered, profile=profile, descriptors=descriptors)


def test_old_library_source_lock_is_not_reinterpreted_as_v2() -> None:
    old_lock = _load("fixtures/node_build_locks/research_compute_node_source_candidate_v1.json")
    with pytest.raises(NodeBuildLockV2Error, match="shape|schema"):
        verify_research_service_build_lock_v2(old_lock)
