from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "verify_economic_os_rc3_local_3node_tcp",
    ROOT / "verify" / "verify_economic_os_rc3_local_3node_tcp.py",
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


def test_canonical_rc3_verifies():
    item = MOD.verify_rc3(MOD.load_rc3(ROOT))
    assert item["digest"] == MOD.EXPECTED_DIGEST
    assert item["testnet_loopback_execution_evidence_digest"] == MOD.EXPECTED_LOOPBACK
    assert item["economic_testnet_status"] == "LOCAL_3_NODE_TCP_PROPAGATION_VERIFIED_NOT_PERSISTENT_EXTERNAL_TESTNET"
    assert item["persistent_external_testnet_claim"] is False


def test_fresh_hash_cannot_promote_to_persistent_external_testnet():
    item = MOD.load_rc3(ROOT)
    item["economic_testnet_status"] = "PERSISTENT_EXTERNAL_TESTNET_EXECUTED"
    item["persistent_external_testnet_claim"] = True
    item = fresh_hash(item)
    with pytest.raises(MOD.EconomicOSRC3Error):
        MOD.verify_rc3(item)


def test_fresh_hash_cannot_remove_live_economic_cycle_blocker():
    item = MOD.load_rc3(ROOT)
    item["blockers"].remove("ONE_LIVE_EXTERNAL_VALUE_TO_NEXT_CAPACITY_EXECUTION_NOT_CAPTURED")
    item = fresh_hash(item)
    with pytest.raises(MOD.EconomicOSRC3Error):
        MOD.verify_rc3(item)


def test_fresh_hash_cannot_replace_loopback_execution_root():
    item = MOD.load_rc3(ROOT)
    item["testnet_loopback_execution_evidence_digest"] = "f" * 64
    item = fresh_hash(item)
    with pytest.raises(MOD.EconomicOSRC3Error):
        MOD.verify_rc3(item)


def test_fresh_hash_cannot_escalate_execution_authority():
    item = MOD.load_rc3(ROOT)
    item["execution_authority"] = "LOOPBACK_RUNNER"
    item = fresh_hash(item)
    with pytest.raises(MOD.EconomicOSRC3Error):
        MOD.verify_rc3(item)
