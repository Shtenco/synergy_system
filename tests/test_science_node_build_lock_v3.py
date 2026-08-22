from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from synergy_system.node_build_lock_v3 import (
    NodeBuildLockV3Error,
    canonical_json,
    verify_science_source_build_lock_v3,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "node_build_locks" / "science_research_node_source_candidate_v3.json"


def _load() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _rehash(payload: dict) -> None:
    body = dict(payload)
    body.pop("lock_digest", None)
    payload["lock_digest"] = hashlib.sha256(canonical_json(body)).hexdigest()


def test_canonical_science_build_lock_v3_is_source_only() -> None:
    lock = _load()
    assert verify_science_source_build_lock_v3(lock) == lock
    assert lock["lock_digest"] == "de35e3f31d85b9ab559180a12535ecdaa58fd70c6d3575d215994064933e1274"
    assert lock["verification_status"] == "SOURCE_IDENTITY_FROZEN_BUILD_NOT_VERIFIED"
    assert lock["execution_authority"] == "NONE"
    assert all(item["build_artifact_digest"] is None for item in lock["services"])
    assert all(item["build_evidence_digest"] is None for item in lock["services"])


def test_v3_upgrades_only_nexus_source_identity() -> None:
    lock = _load()
    by_id = {item["service_id"]: item for item in lock["services"]}
    assert by_id["nexus"]["source_commit"] == "2ee8f2a29ad2497afca6c7386375a296cd0bdbcf"
    assert by_id["nexus"]["source_ref"] == "feat/smallworld-exact-stdlib-v2-20260822"
    assert by_id["nexus"]["source_role"] == "NEXUS_SMALLWORLD_EXACT_STDLIB_SERVICE_CANDIDATE"

    assert by_id["content-cache"]["source_commit"] == "874a83b6510420ec43ce99fc4b7936e106ad2339"
    assert by_id["synergynet"]["source_commit"] == "874a83b6510420ec43ce99fc4b7936e106ad2339"
    assert by_id["science-agent"]["source_commit"] == "0607690c3036d2fdce2ac3e044094a8e4da0311b"


def test_fresh_hash_cannot_restore_old_numpy_nexus_source() -> None:
    lock = _load()
    nexus = next(item for item in lock["services"] if item["service_id"] == "nexus")
    nexus["source_commit"] = "ef1a6e3675e53fda4bf91566aec61f1b62fa9336"
    nexus["source_ref"] = "feat/smallworld-service-protocol-v1-20260821"
    nexus["source_role"] = "NEXUS_SMALLWORLD_SERVICE_CANDIDATE"
    _rehash(lock)
    with pytest.raises(NodeBuildLockV3Error):
        verify_science_source_build_lock_v3(lock)


def test_fresh_hash_cannot_claim_build_evidence_or_execution() -> None:
    lock = _load()
    lock["services"][0]["build_artifact_digest"] = "1" * 64
    lock["services"][0]["build_status"] = "BUILD_ARTIFACT_FROZEN_TESTS_PENDING"
    _rehash(lock)
    with pytest.raises(NodeBuildLockV3Error):
        verify_science_source_build_lock_v3(lock)

    lock = _load()
    lock["execution_authority"] = "META_OS"
    _rehash(lock)
    with pytest.raises(NodeBuildLockV3Error):
        verify_science_source_build_lock_v3(lock)


def test_service_order_and_coverage_are_exact() -> None:
    lock = _load()
    lock["services"] = list(reversed(lock["services"]))
    _rehash(lock)
    with pytest.raises(NodeBuildLockV3Error):
        verify_science_source_build_lock_v3(lock)

    lock = _load()
    lock["services"].pop()
    _rehash(lock)
    with pytest.raises(NodeBuildLockV3Error):
        verify_science_source_build_lock_v3(lock)
