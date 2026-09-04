from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "live_economic_cycle_capture_v1",
    ROOT / "src" / "synergy_system" / "live_economic_cycle_capture_v1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def candidate():
    phases = []
    for ordinal, phase, owner, schema, needs_external in MOD.PHASES:
        item = {
            "ordinal": ordinal,
            "phase": phase,
            "owner": owner,
            "schema": schema,
            "artifact_digest": f"{ordinal:064x}",
            "observed_at": f"2026-08-28T12:{ordinal:02d}:00Z",
        }
        if needs_external:
            item["external_evidence"] = {
                "provider": f"ExternalProvider{ordinal}",
                "provider_reference": f"provider-reference-{ordinal}",
                "environment": "LIVE_EXTERNAL",
                "provider_evidence_digest": f"{100 + ordinal:064x}",
                "verification_status": "PENDING_EXTERNAL_VERIFICATION",
            }
        if phase == "HUMAN_GOVERNANCE_HANDOFF":
            item["decision_authority"] = "MULTISIG_GOVERNANCE"
            item["ai_authority"] = "NONE"
        if phase == "LATER_SETTLEMENT_REVERSAL":
            item["authorization_consumption"] = "REMAINS_CONSUMED"
        phases.append(item)
    value = {
        "schema": MOD.SCHEMA,
        "run_id": "structural-test-only-not-live-evidence",
        "economic_cycle_v1_digest": MOD.ECONOMIC_CYCLE_V1,
        "economic_os_rc4_digest": MOD.ECONOMIC_OS_RC4,
        "started_at": "2026-08-28T12:00:00Z",
        "completed_at": "2026-08-28T12:20:00Z",
        "phases": phases,
        "canonical_hard_nav_before": "100",
        "canonical_hard_nav_after": "102",
        "realized_external_pnl_before": "-5",
        "realized_external_pnl_after": "-3",
        "next_cycle_final_available_capacity": "1",
        "next_cycle_capacity_status": "CAPACITY_AVAILABLE",
        "internal_mint_or_revaluation_counted_as_profit": "0",
        "capture_status": "STRUCTURALLY_COMPLETE_PENDING_EXTERNAL_VERIFICATION",
        "external_verification_status": "PENDING",
        "live_execution_claim": False,
        "authority": "PROVENANCE_ONLY",
        "execution_authority": "NONE",
        "ai_authority": "NONE",
        "blockchain_submission_authority": "NONE",
    }
    value["digest"] = MOD.canonical_digest(value)
    return value


def rehash(value):
    body = dict(value)
    body.pop("digest", None)
    value["digest"] = MOD.canonical_digest(body)
    return value


def test_structural_candidate_allows_negative_pnl_baseline_with_positive_delta():
    item = candidate()
    result = MOD.verify_live_economic_cycle_capture_candidate_v1(item)
    assert result["capture_status"] == "STRUCTURALLY_COMPLETE_PENDING_EXTERNAL_VERIFICATION"
    assert result["live_execution_claim"] is False


def test_mock_external_reference_is_rejected():
    item = candidate()
    item["phases"][0]["external_evidence"]["provider_reference"] = "MOCK-provider-reference"
    rehash(item)
    with pytest.raises(MOD.LiveEconomicCycleCaptureV1Error, match="admissible live-external"):
        MOD.verify_live_economic_cycle_capture_candidate_v1(item)


def test_candidate_cannot_self_promote_to_live_verified():
    item = candidate()
    item["capture_status"] = "LIVE_EXTERNAL_VALUE_TO_NEXT_CAPACITY_VERIFIED"
    item["external_verification_status"] = "VERIFIED"
    item["live_execution_claim"] = True
    rehash(item)
    with pytest.raises(MOD.LiveEconomicCycleCaptureV1Error):
        MOD.verify_live_economic_cycle_capture_candidate_v1(item)


def test_phase_reordering_is_rejected():
    item = candidate()
    item["phases"][0], item["phases"][1] = item["phases"][1], item["phases"][0]
    rehash(item)
    with pytest.raises(MOD.LiveEconomicCycleCaptureV1Error, match="phase fields mismatch: EXTERNAL_VALUE_EVIDENCE"):
        MOD.verify_live_economic_cycle_capture_candidate_v1(item)


def test_ai_governance_is_rejected():
    item = candidate()
    handoff = item["phases"][5]
    handoff["decision_authority"] = "AI_AUTONOMOUS"
    handoff["ai_authority"] = "AUTONOMOUS"
    rehash(item)
    with pytest.raises(MOD.LiveEconomicCycleCaptureV1Error, match="governance authority"):
        MOD.verify_live_economic_cycle_capture_candidate_v1(item)


def test_reversal_cannot_revive_authorization():
    item = candidate()
    item["phases"][8]["authorization_consumption"] = "REVIVED"
    rehash(item)
    with pytest.raises(MOD.LiveEconomicCycleCaptureV1Error, match="authorization"):
        MOD.verify_live_economic_cycle_capture_candidate_v1(item)


def test_hard_nav_must_grow():
    item = candidate()
    item["canonical_hard_nav_after"] = item["canonical_hard_nav_before"]
    rehash(item)
    with pytest.raises(MOD.LiveEconomicCycleCaptureV1Error, match="HardNAV"):
        MOD.verify_live_economic_cycle_capture_candidate_v1(item)


def test_realized_external_pnl_must_improve():
    item = candidate()
    item["realized_external_pnl_after"] = item["realized_external_pnl_before"]
    rehash(item)
    with pytest.raises(MOD.LiveEconomicCycleCaptureV1Error, match="external P&L"):
        MOD.verify_live_economic_cycle_capture_candidate_v1(item)


def test_next_capacity_must_be_positive():
    item = candidate()
    item["next_cycle_final_available_capacity"] = "0"
    rehash(item)
    with pytest.raises(MOD.LiveEconomicCycleCaptureV1Error, match="capacity"):
        MOD.verify_live_economic_cycle_capture_candidate_v1(item)


def test_internal_revaluation_cannot_be_counted_as_profit():
    item = candidate()
    item["internal_mint_or_revaluation_counted_as_profit"] = "1"
    rehash(item)
    with pytest.raises(MOD.LiveEconomicCycleCaptureV1Error, match="internal value counted as profit"):
        MOD.verify_live_economic_cycle_capture_candidate_v1(item)


def test_hidden_top_level_live_verified_field_is_rejected_even_after_fresh_rehash():
    item = candidate()
    item["live_verified"] = True
    rehash(item)
    with pytest.raises(MOD.LiveEconomicCycleCaptureV1Error, match="capture top-level fields mismatch"):
        MOD.verify_live_economic_cycle_capture_candidate_v1(item)


def test_hidden_phase_execution_authority_is_rejected_even_after_fresh_rehash():
    item = candidate()
    item["phases"][1]["execution_authority"] = "AI"
    rehash(item)
    with pytest.raises(MOD.LiveEconomicCycleCaptureV1Error, match="phase fields mismatch"):
        MOD.verify_live_economic_cycle_capture_candidate_v1(item)


def test_hidden_external_provider_verified_field_is_rejected_even_after_fresh_rehash():
    item = candidate()
    item["phases"][0]["external_evidence"]["provider_verified"] = True
    rehash(item)
    with pytest.raises(MOD.LiveEconomicCycleCaptureV1Error, match="external evidence fields mismatch"):
        MOD.verify_live_economic_cycle_capture_candidate_v1(item)
