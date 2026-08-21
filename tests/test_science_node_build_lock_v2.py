from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from synergy_system.node_build_lock_v2 import NodeBuildLockV2Error, lock_digest, verify_node_build_lock_v2, verify_science_source_build_lock_v2


FIXTURE = Path("fixtures/node_build_locks/science_research_node_source_candidate_v2.json")


def load_fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_science_source_lock_is_exact_and_not_build_verified():
    payload = verify_science_source_build_lock_v2(load_fixture())
    assert payload["lock_digest"] == "24e4a3c6ed23c2e156b07821fb3b1e0e232651c256bc3b750d2ed25bee477757"
    assert payload["verification_status"] == "SOURCE_IDENTITY_FROZEN_BUILD_NOT_VERIFIED"
    assert all(item["build_artifact_digest"] is None for item in payload["services"])


def test_fresh_hash_cannot_turn_source_candidate_into_verified_science_build():
    payload = load_fixture()
    payload["services"][0]["build_artifact_digest"] = "11" * 32
    payload["services"][0]["build_evidence_digest"] = "22" * 32
    payload["services"][0]["build_status"] = "BUILD_VERIFIED"
    payload["verification_status"] = "BUILD_EVIDENCE_INCOMPLETE"
    payload["lock_digest"] = lock_digest(payload)
    verify_node_build_lock_v2(payload)
    with pytest.raises(NodeBuildLockV2Error):
        verify_science_source_build_lock_v2(payload)


def test_wrong_nexus_commit_fails_even_with_fresh_digest():
    payload = load_fixture()
    for service in payload["services"]:
        if service["service_id"] == "nexus":
            service["source_commit"] = "0" * 40
    payload["lock_digest"] = lock_digest(payload)
    with pytest.raises(NodeBuildLockV2Error):
        verify_science_source_build_lock_v2(payload)


def test_build_status_and_digest_presence_are_consistent():
    payload = copy.deepcopy(load_fixture())
    payload["services"][0]["build_artifact_digest"] = "11" * 32
    payload["lock_digest"] = lock_digest(payload)
    with pytest.raises(NodeBuildLockV2Error):
        verify_node_build_lock_v2(payload)
