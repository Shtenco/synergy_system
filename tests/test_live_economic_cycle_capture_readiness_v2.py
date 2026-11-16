from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from verify.verify_live_economic_cycle_capture_readiness_v2 import (
    ReadinessV2Error,
    canonical_digest,
    verify_readiness_v2,
)

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "live_economic_cycle_capture_readiness_v2.json"


def evidence():
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def fresh_hash(value):
    value["digest"] = canonical_digest(value)
    return value


def test_readiness_v2_is_pinned_and_non_live():
    result = verify_readiness_v2(evidence())
    assert result["status"] == "PASS"
    assert result["live_execution_claim"] is False
    assert result["external_verification_status"] == "NOT_EXECUTED"


def test_fresh_hash_cannot_promote_status_to_live():
    value = evidence()
    value["capture_protocol_status"] = "LIVE_EXTERNAL_VALUE_TO_NEXT_CAPACITY_VERIFIED"
    value["live_execution_claim"] = True
    fresh_hash(value)
    with pytest.raises(ReadinessV2Error):
        verify_readiness_v2(value)


def test_fresh_hash_cannot_replace_implementation_identity():
    value = evidence()
    value["implementation_blob_sha"] = "0" * 64
    fresh_hash(value)
    with pytest.raises(ReadinessV2Error):
        verify_readiness_v2(value)


def test_fresh_hash_cannot_replace_test_identity():
    value = evidence()
    value["test_blob_sha"] = "0" * 64
    fresh_hash(value)
    with pytest.raises(ReadinessV2Error):
        verify_readiness_v2(value)


def test_fresh_hash_cannot_replace_targeted_audit_root_or_scope():
    value = evidence()
    value["targeted_metapay_audit_digest"] = "0" * 64
    value["targeted_metapay_audit_scope"] = "EXHAUSTIVE"
    fresh_hash(value)
    with pytest.raises(ReadinessV2Error):
        verify_readiness_v2(value)


def test_fresh_hash_cannot_remove_live_cycle_blocker():
    value = evidence()
    value["current_blocker"] = "NONE"
    value["blocker_removed"] = True
    fresh_hash(value)
    with pytest.raises(ReadinessV2Error):
        verify_readiness_v2(value)


def test_fresh_hash_cannot_escalate_authority():
    value = evidence()
    value["execution_authority"] = "AI"
    value["ai_authority"] = "AUTONOMOUS"
    fresh_hash(value)
    with pytest.raises(ReadinessV2Error):
        verify_readiness_v2(value)


def test_fresh_hash_cannot_relabel_known_fixture_as_live():
    value = evidence()
    value["inadmissible_known_candidates"][0]["classification"] = "LIVE_SETTLEMENT_EVIDENCE"
    fresh_hash(value)
    with pytest.raises(ReadinessV2Error):
        verify_readiness_v2(value)
