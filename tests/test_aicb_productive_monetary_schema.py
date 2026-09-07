import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


SCHEMA_PATH = Path("schemas/aicb_productive_monetary_v1.json")


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
