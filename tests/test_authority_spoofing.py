from pathlib import Path
from uuid import uuid4

import pytest

from synergy_contracts.validation import ContractValidationError, ContractValidator, canonical_payload_hash


ROOT = Path(__file__).resolve().parents[1]
validator = ContractValidator(ROOT / "schemas")


def base_intent():
    payload = {
        "strategy_id": "MIDAS-V32.1",
        "instrument": "EURUSD",
        "side": "BUY",
        "quantity": 100000,
        "max_total_cost": 45.0,
        "settlement_date": "2026-09-08",
        "venue_constraints": ["prefunded"],
        "risk_budget_ref": "risk:fx:1",
        "expected_edge_bps": 4.2,
    }
    return {
        "schema_id": "synergy.contract-envelope/v1",
        "contract_type": "TradingExecutionIntent",
        "contract_version": 1,
        "contract_id": str(uuid4()),
        "created_at": "2026-09-06T10:00:00Z",
        "producer": {"repo": "Shtenco/midas_ai", "component": "portfolio-executor", "authority": "trading_intelligence"},
        "consumer": {"repo": "Shtenco/synergy_pay_system", "component": "execution-router", "authority": "payment_execution_settlement"},
        "correlation_id": str(uuid4()),
        "causation_id": None,
        "provenance": {
            "code_commit": "abcdef1",
            "model_id": "MIDAS-V32.1",
            "data_cutoff": "2026-09-06T09:59:00Z",
            "epistemic_state": "INFERRED",
            "source_refs": ["signal:test"],
        },
        "authorization": {
            "required_authority": "trading_execution",
            "decision": "APPROVED",
            "granted_by": "risk-governor",
            "grant_ref": "approval:test",
        },
        "evidence": {"hash_alg": "sha256", "payload_hash": canonical_payload_hash(payload), "refs": ["signal:test"]},
        "payload": payload,
    }


def test_spoofed_producer_repo_is_rejected():
    contract = base_intent()
    contract["producer"]["repo"] = "Shtenco/agi_nexus"
    with pytest.raises(ContractValidationError, match="producer repo"):
        validator.validate(contract, "midas_metapay_financial_v1.json")


def test_spoofed_consumer_authority_is_rejected():
    contract = base_intent()
    contract["consumer"]["authority"] = "trading_intelligence"
    with pytest.raises(ContractValidationError, match="consumer authority"):
        validator.validate(contract, "midas_metapay_financial_v1.json")
