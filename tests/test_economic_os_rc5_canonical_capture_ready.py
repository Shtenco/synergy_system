from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("verify_rc5", ROOT / "verify" / "verify_economic_os_rc5_canonical_capture_ready.py")
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def load():
    return json.loads((ROOT / "releases" / "economic_os_rc5_canonical_capture_ready_20260828.json").read_text(encoding="utf-8"))


def rehash(value):
    body = dict(value); body.pop("digest", None)
    value["digest"] = MOD.digest(body)
    return value


def test_rc5_exact_release_verifies():
    item = MOD.verify_rc5(load())
    assert item["digest"] == MOD.EXPECTED_DIGEST
    assert item["canonical_prs_mergeable_count"] == 4
    assert item["live_execution_claim"] is False


def test_fresh_hash_cannot_claim_main_promotion():
    item = copy.deepcopy(load())
    item["canonicalization_status"] = "MERGED_TO_MAIN"
    item["blockers"].remove("CANONICAL_MAIN_PROMOTION_NOT_EXECUTED")
    rehash(item)
    with pytest.raises(MOD.RC5VerificationError): MOD.verify_rc5(item)


def test_fresh_hash_cannot_claim_live_cycle():
    item = copy.deepcopy(load())
    item["live_cycle_capture_status"] = "LIVE_EXTERNAL_VALUE_TO_NEXT_CAPACITY_VERIFIED"
    item["live_execution_claim"] = True
    item["blockers"].remove("ONE_LIVE_EXTERNAL_VALUE_TO_NEXT_CAPACITY_EXECUTION_NOT_CAPTURED")
    rehash(item)
    with pytest.raises(MOD.RC5VerificationError): MOD.verify_rc5(item)


def test_fresh_hash_cannot_claim_external_testnet():
    item = copy.deepcopy(load())
    item["economic_testnet_status"] = "EXTERNAL_MULTI_NODE_TESTNET_EXECUTED"
    item["external_host_testnet_claim"] = True
    rehash(item)
    with pytest.raises(MOD.RC5VerificationError): MOD.verify_rc5(item)


def test_authority_cannot_escalate():
    item = copy.deepcopy(load())
    item["ai_authority"] = "AUTONOMOUS"
    item["blockchain_submission_authority"] = "ENABLED"
    rehash(item)
    with pytest.raises(MOD.RC5VerificationError): MOD.verify_rc5(item)
