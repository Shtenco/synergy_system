from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("verify_rc4", ROOT / "verify" / "verify_economic_os_rc4_local_persistence_restart.py")
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def load():
    return json.loads((ROOT / "releases" / "economic_os_rc4_local_persistence_restart_20260828.json").read_text(encoding="utf-8"))


def rehash(value):
    body = dict(value); body.pop("digest", None)
    value["digest"] = MOD.digest(body)
    return value


def test_rc4_exact_release_verifies():
    item = MOD.verify_rc4(load())
    assert item["digest"] == MOD.EXPECTED_DIGEST
    assert item["testnet_persistent_restart_execution_evidence_digest"] == MOD.EXPECTED_PERSISTENCE_EVIDENCE
    assert item["external_host_testnet_claim"] is False


def test_fresh_hash_cannot_promote_external_testnet():
    item = copy.deepcopy(load())
    item["external_host_testnet_claim"] = True
    item["economic_testnet_status"] = "EXTERNAL_TESTNET_EXECUTED"
    rehash(item)
    with pytest.raises(MOD.RC4VerificationError):
        MOD.verify_rc4(item)


def test_fresh_hash_cannot_remove_live_cycle_blocker():
    item = copy.deepcopy(load())
    item["blockers"].remove("ONE_LIVE_EXTERNAL_VALUE_TO_NEXT_CAPACITY_EXECUTION_NOT_CAPTURED")
    rehash(item)
    with pytest.raises(MOD.RC4VerificationError):
        MOD.verify_rc4(item)


def test_fresh_hash_cannot_grant_ai_or_submission_authority():
    item = copy.deepcopy(load())
    item["ai_authority"] = "AUTONOMOUS"
    item["blockchain_submission_authority"] = "ENABLED"
    rehash(item)
    with pytest.raises(MOD.RC4VerificationError):
        MOD.verify_rc4(item)


def test_persistence_evidence_root_is_immutable():
    item = copy.deepcopy(load())
    item["testnet_persistent_restart_execution_evidence_digest"] = "0" * 64
    rehash(item)
    with pytest.raises(MOD.RC4VerificationError):
        MOD.verify_rc4(item)
