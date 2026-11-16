from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "verify_economic_os_rc2_local_testnet_execution",
    ROOT / "verify" / "verify_economic_os_rc2_local_testnet_execution.py",
)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def fresh_hash(payload):
    body = dict(payload)
    body.pop("digest", None)
    body["digest"] = MOD.digest(body)
    return body


def test_canonical_rc2_verifies():
    item = MOD.verify_rc2(MOD.load_rc2(ROOT))
    assert item["digest"] == MOD.EXPECTED_DIGEST
    assert item["economic_testnet_status"] == "LOCAL_PROTOCOL_EXECUTION_VERIFIED_NETWORK_NOT_EXECUTED"
    assert item["live_execution_claim"] is False
    assert item["network_testnet_claim"] is False
    assert item["testnet_local_execution_evidence_digest"] == MOD.EXPECTED_LOCAL_EXECUTION


def test_fresh_hash_cannot_promote_network_testnet():
    item = MOD.load_rc2(ROOT)
    item["economic_testnet_status"] = "NETWORK_TESTNET_EXECUTED"
    item["network_testnet_claim"] = True
    item = fresh_hash(item)
    with pytest.raises(MOD.EconomicOSRC2Error):
        MOD.verify_rc2(item)


def test_fresh_hash_cannot_remove_live_cycle_blocker():
    item = MOD.load_rc2(ROOT)
    item["blockers"].remove("ONE_LIVE_EXTERNAL_VALUE_TO_NEXT_CAPACITY_EXECUTION_NOT_CAPTURED")
    item = fresh_hash(item)
    with pytest.raises(MOD.EconomicOSRC2Error):
        MOD.verify_rc2(item)


def test_fresh_hash_cannot_replace_local_execution_evidence():
    item = MOD.load_rc2(ROOT)
    item["testnet_local_execution_evidence_digest"] = "0" * 64
    item = fresh_hash(item)
    with pytest.raises(MOD.EconomicOSRC2Error):
        MOD.verify_rc2(item)


def test_fresh_hash_cannot_escalate_authority():
    item = MOD.load_rc2(ROOT)
    item["blockchain_submission_authority"] = "TESTNET_RUNNER"
    item = fresh_hash(item)
    with pytest.raises(MOD.EconomicOSRC2Error):
        MOD.verify_rc2(item)
