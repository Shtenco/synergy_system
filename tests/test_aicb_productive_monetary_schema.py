import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


SCHEMA_PATH = Path("schemas/aicb_productive_monetary_v1.json")
FLOW_PATH = Path("config/aicb_productive_monetary_flow_v1.json")


def load_def(name: str):
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return schema["$defs"][name]


def test_target_emission_proposal_schema_accepts_bounded_proposal():
    payload = {
        "period_id": "2026-09",
        "requested_emission": 100.0,
        "raw_policy_limit": 120.0,
        "matching_capital_limit": 100.0,
        "policy_score": 0.75,
        "blocked": False,
        "block_reason": "",
        "policy_version": "AICB_V5_DUAL_GATE_1",
    }
    Draft202012Validator(load_def("TargetEmissionProposalV5")).validate(payload)


def test_productive_attestation_rejects_nonzero_physical_gap():
    payload = {
        "close_id": "prod-close-1",
        "close_sequence": 1,
        "project_ids": ["p1"],
        "goods_output_growth_units": 10.0,
        "capacity_growth_units": 5.0,
        "verified_goods_value_growth": 100.0,
        "verified_capacity_value_growth": 50.0,
        "fraud_or_quality_haircut_value": 0.0,
        "physical_consistency_gap": 1.0,
        "valuation_method_ref": "valuation:v1",
        "evidence_refs": ["evidence:p1"],
        "credited_productive_growth": 150.0,
    }
    with pytest.raises(Exception):
        Draft202012Validator(load_def("ProductiveGrowthAttestation")).validate(payload)


def test_dual_release_receipt_keeps_two_consumed_credits_explicit():
    payload = {
        "proposal_id": "proposal-1",
        "financial_growth_consumed": 80.0,
        "productive_growth_consumed": 80.0,
        "released_emission": 40.0,
        "release_status": "PARTIAL",
    }
    Draft202012Validator(load_def("DualGateReleaseReceipt")).validate(payload)


def test_release_accounting_recognition_forbids_mint_profit():
    payload = {
        "proposal_id": "proposal-1",
        "release_tx_ref": "sandbox:tx:1",
        "financial_growth_attestation_ref": "financial:close:2",
        "productive_growth_attestation_ref": "productive:close:1",
        "released_units": 40.0,
        "unit_value": 1.0,
        "released_monetary_value": 40.0,
        "accounting_classification": "MONETARY_LIABILITY",
        "recognition_status": "RECOGNIZED",
        "recognized_revenue": 0,
        "recognized_profit": 0,
    }
    Draft202012Validator(load_def("EmissionReleaseRecognition")).validate(payload)
    bad = dict(payload, recognized_profit=40.0)
    with pytest.raises(Exception):
        Draft202012Validator(load_def("EmissionReleaseRecognition")).validate(bad)


def test_reference_e2e_vector_obeys_two_key_release_and_coverage():
    """Reference V5 transaction without claiming a live cross-repo deployment."""
    proposal = {
        "period_id": "2026-09",
        "requested_emission": 100.0,
        "raw_policy_limit": 120.0,
        "matching_capital_limit": 100.0,
        "policy_score": 0.75,
        "blocked": False,
        "block_reason": "",
        "policy_version": "AICB_V5_DUAL_GATE_1",
    }
    productive = {
        "close_id": "prod-close-1",
        "close_sequence": 1,
        "project_ids": ["factory-1"],
        "goods_output_growth_units": 100.0,
        "capacity_growth_units": 20.0,
        "verified_goods_value_growth": 70.0,
        "verified_capacity_value_growth": 30.0,
        "fraud_or_quality_haircut_value": 20.0,
        "physical_consistency_gap": 0,
        "valuation_method_ref": "valuation:independent:v1",
        "evidence_refs": ["warehouse:acceptance:1", "equipment:commissioning:1"],
        "credited_productive_growth": 80.0,
    }
    financial = {
        "close_id": "financial-close-2",
        "close_sequence": 2,
        "previous_hardnav": 1000.0,
        "current_hardnav": 1090.0,
        "previous_liabilities": 100.0,
        "current_liabilities": 110.0,
        "eligible_asset_gross_growth": 100.0,
        "internal_mark_change": 0.0,
        "flash_principal_inflow": 0.0,
        "eligible_asset_classes": ["VERIFIED_PRODUCTIVE_ASSET"],
        "evidence_refs": ["financial:ledger:2"],
        "credited_growth": 90.0,
    }

    Draft202012Validator(load_def("TargetEmissionProposalV5")).validate(proposal)
    Draft202012Validator(load_def("ProductiveGrowthAttestation")).validate(productive)
    Draft202012Validator(load_def("EligibleAssetGrowthAttestation")).validate(financial)

    coverage_ratio = 2.0
    dual_credit = min(productive["credited_productive_growth"], financial["credited_growth"])
    required_growth = proposal["requested_emission"] * coverage_ratio
    released_units = proposal["requested_emission"] * dual_credit / required_growth
    # 80 value of weaker evidence against 200 required backing releases 40 units.
    assert dual_credit == 80.0
    assert required_growth == 200.0
    assert released_units == 40.0

    receipt = {
        "proposal_id": "proposal-1",
        "financial_growth_consumed": dual_credit,
        "productive_growth_consumed": dual_credit,
        "released_emission": released_units,
        "release_status": "PARTIAL",
    }
    Draft202012Validator(load_def("DualGateReleaseReceipt")).validate(receipt)
    assert receipt["financial_growth_consumed"] == receipt["productive_growth_consumed"]
    assert receipt["released_emission"] * coverage_ratio <= dual_credit

    recognition = {
        "proposal_id": "proposal-1",
        "release_tx_ref": "sandbox:tx:1",
        "financial_growth_attestation_ref": financial["close_id"],
        "productive_growth_attestation_ref": productive["close_id"],
        "released_units": released_units,
        "unit_value": 1.0,
        "released_monetary_value": released_units,
        "accounting_classification": "MONETARY_LIABILITY",
        "recognition_status": "RECOGNIZED",
        "recognized_revenue": 0,
        "recognized_profit": 0,
    }
    Draft202012Validator(load_def("EmissionReleaseRecognition")).validate(recognition)


def test_flow_registry_keeps_ai_proposal_only():
    flow = json.loads(FLOW_PATH.read_text(encoding="utf-8"))
    policy = flow["authorities"]["policy_proposal"]
    assert policy["authority_status"] == "PROPOSAL_ONLY_RND"
    assert policy["may_mint"] is False
    assert policy["may_attest"] is False
    assert policy["may_release"] is False
    assert flow["hard_firewall"]["one_sided_evidence_can_release"] is False
