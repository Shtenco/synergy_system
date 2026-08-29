import json
from pathlib import Path

import pytest

from synergy_system.node_build_lock_v1 import (
    NodeBuildLockError,
    lock_digest,
    verify_research_source_build_lock,
)

ROOT = Path(__file__).resolve().parents[1]


def load_lock():
    return json.loads((ROOT / "fixtures/node_build_locks/research_compute_node_source_candidate_v1.json").read_text(encoding="utf-8"))


def test_canonical_source_lock_has_fixed_digest_and_no_build_claim():
    payload = load_lock()
    verify_research_source_build_lock(payload)
    assert lock_digest(payload) == "14c763218602585d49e12060e1e6cf21d33815fda0cb18711a6522a26157ace2"
    assert all(service["build_artifact_digest"] is None for service in payload["services"])
    assert payload["verification_status"] == "SOURCE_IDENTITY_FROZEN_BUILD_NOT_VERIFIED"
    assert payload["execution_authority"] == "NONE"


def test_fresh_hash_cannot_relabel_other_nexus_commit_as_candidate():
    payload = load_lock()
    payload["services"][1]["source_commit"] = "0" * 40
    payload["lock_digest"] = lock_digest(payload)
    with pytest.raises(NodeBuildLockError, match="source identity drifted"):
        verify_research_source_build_lock(payload)


def test_source_lock_cannot_invent_build_artifact_with_fresh_hash():
    payload = load_lock()
    payload["services"][0]["build_artifact_digest"] = "a" * 64
    payload["services"][0]["build_status"] = "BUILD_VERIFIED"
    payload["lock_digest"] = lock_digest(payload)
    with pytest.raises(NodeBuildLockError, match="cannot claim a built artifact"):
        verify_research_source_build_lock(payload)


def test_source_lock_cannot_gain_execution_authority():
    payload = load_lock()
    payload["execution_authority"] = "META_OS"
    payload["lock_digest"] = lock_digest(payload)
    with pytest.raises(NodeBuildLockError, match="cannot execute"):
        verify_research_source_build_lock(payload)


def test_source_lock_is_bound_to_exact_profile_digest():
    payload = load_lock()
    payload["profile_digest"] = "b" * 64
    payload["lock_digest"] = lock_digest(payload)
    with pytest.raises(NodeBuildLockError, match="wrong node profile"):
        verify_research_source_build_lock(payload)
