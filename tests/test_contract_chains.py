from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from uuid import uuid4

import pytest

from synergy_contracts.validation import ContractValidationError, ContractValidator, canonical_payload_hash


SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schemas"
validator = ContractValidator(SCHEMA_DIR)


def make_contract(contract_type, producer, consumer, payload, correlation_id, causation_id=None, auth_decision="APPROVED", required_authority="domain_authority"):
    cid = str(uuid4())
    return {
        "schema_id": "synergy.contract-envelope/v1",
        "contract_type": contract_type,
        "contract_version": 1,
        "contract_id": cid,
        "created_at": "2026-09-06T10:00:00Z",
        "producer": producer,
        "consumer": consumer,
        "correlation_id": correlation_id,
        "causation_id": causation_id,
        "provenance": {
            "code_commit": "abcdef1",
            "model_id": None,
            "data_cutoff": "2026-09-06T09:59:00Z",
            "epistemic_state": "KNOWN",
            "source_refs": ["test:evidence"]
        },
        "authorization": {
            "required_authority": required_authority,
            "decision": auth_decision,
            "granted_by": "test-authority" if auth_decision == "APPROVED" else None,
            "grant_ref": "test:grant" if auth_decision == "APPROVED" else None
        },
        "evidence": {
            "hash_alg": "sha256",
            "payload_hash": canonical_payload_hash(payload),
            "refs": ["test:evidence"]
        },
        "payload": payload
    }


def endpoint(repo, component, authority):
    return {"repo": repo, "component": component, "authority": authority}


def test_nexus_to_autopilot_chain():
    corr = str(uuid4())
    proposal = make_contract(
        "NexusPolicyProposal",
        endpoint("Shtenco/agi_nexus", "reasoner", "reasoning_core"),
        endpoint("Shtenco/agi_autopilot", "policy-engine", "action_orchestration"),
        {
            "proposal_id": str(uuid4()),
            "domain": "finance",
            "objective": "Evaluate a bounded execution proposal",
            "recommended_action": "Request domain approval",
            "confidence": 0.82,
            "constraints": ["no-direct-execution"],
            "risk_flags": ["capital-at-risk"],
            "expires_at": "2026-09-06T11:00:00Z"
        },
        corr,
        auth_decision="PROPOSAL_ONLY",
        required_authority="action_orchestration"
    )
    decision = make_contract(
        "AutopilotPolicyDecision",
        endpoint("Shtenco/agi_autopilot", "policy-engine", "action_orchestration"),
        endpoint("Shtenco/synergy_financial_os", "authorization-gateway", "canonical_accounting"),
        {
            "proposal_id": proposal["payload"]["proposal_id"],
            "decision": "REQUIRE_APPROVAL",
            "policy_id": "finance-capital-v1",
            "capabilities": ["submit-finance-proposal"],
            "required_approvals": ["financial_authority"],
            "reason": "NEXUS is advisory only"
        },
        corr,
        proposal["contract_id"],
        auth_decision="NOT_REQUIRED",
        required_authority="action_orchestration"
    )
    validator.validate(proposal, "nexus_autopilot_v1.json")
    validator.validate(decision, "nexus_autopilot_v1.json")
    validator.validate_chain([proposal, decision])


def test_midas_to_metapay_to_financial_chain():
    corr = str(uuid4())
    intent = make_contract(
        "TradingExecutionIntent",
        endpoint("Shtenco/midas_ai", "portfolio-executor", "trading_intelligence"),
        endpoint("Shtenco/synergy_pay_system", "execution-router", "payment_execution_settlement"),
        {
            "strategy_id": "MIDAS-V32.1",
            "instrument": "EURUSD",
            "side": "BUY",
            "quantity": 100000,
            "max_total_cost": 45.0,
            "settlement_date": "2026-09-08",
            "venue_constraints": ["prefunded"],
            "risk_budget_ref": "risk:2026-09-06:fx",
            "expected_edge_bps": 4.2
        },
        corr,
        auth_decision="APPROVED",
        required_authority="trading_execution"
    )
    settlement = make_contract(
        "SettlementEvidence",
        endpoint("Shtenco/synergy_pay_system", "settlement", "payment_execution_settlement"),
        endpoint("Shtenco/synergy_financial_os", "reconciliation", "canonical_accounting"),
        {
            "execution_intent_id": intent["contract_id"],
            "status": "SETTLED",
            "asset": "USD",
            "gross_amount": 100420.0,
            "fees": 20.0,
            "net_amount": 100400.0,
            "external_reference": "broker-fill-123",
            "settled_at": "2026-09-06T10:00:05Z",
            "counterparty": "broker"
        },
        corr,
        intent["contract_id"],
        auth_decision="NOT_REQUIRED",
        required_authority="payment_execution_settlement"
    )
    result = make_contract(
        "ReconciledTradingResult",
        endpoint("Shtenco/synergy_financial_os", "reconciliation", "canonical_accounting"),
        endpoint("Shtenco/midas_ai", "performance-ledger", "trading_intelligence"),
        {
            "execution_intent_id": intent["contract_id"],
            "settlement_contract_id": settlement["contract_id"],
            "realized_pnl": 400.0,
            "hardnav_delta": 400.0,
            "reconciliation_status": "MATCHED"
        },
        corr,
        settlement["contract_id"],
        auth_decision="NOT_REQUIRED",
        required_authority="canonical_accounting"
    )
    for contract in [intent, settlement, result]:
        validator.validate(contract, "midas_metapay_financial_v1.json")
    validator.validate_chain([intent, settlement, result])


def test_science_to_eurasian_to_financial_chain():
    corr = str(uuid4())
    candidate = make_contract(
        "CommercializationCandidate",
        endpoint("Shtenco/nexus_science_agent", "commercialization-gate", "science_research_orchestration"),
        endpoint("Shtenco/synergy_eurasian", "project-model", "productive_project_model"),
        {
            "candidate_id": str(uuid4()),
            "technology": "validated-industrial-process",
            "hypothesis_status": "SUPPORTED",
            "trl": 6,
            "reproduction_status": "INDEPENDENT",
            "evidence_refs": ["exp:001", "replication:002"],
            "target_industries": ["manufacturing"]
        },
        corr,
        auth_decision="NOT_REQUIRED",
        required_authority="science_research_orchestration"
    )
    project = make_contract(
        "ProductiveProjectProposal",
        endpoint("Shtenco/synergy_eurasian", "project-model", "productive_project_model"),
        endpoint("Shtenco/synergy_financial_os", "underwriting", "canonical_accounting"),
        {
            "project_id": str(uuid4()),
            "candidate_id": candidate["payload"]["candidate_id"],
            "region": "pilot-region",
            "industry": "manufacturing",
            "capex": 1_000_000,
            "opex_annual": 300_000,
            "expected_external_revenue": 650_000,
            "jobs": 25,
            "stress_case": {"revenue_haircut": 0.35},
            "funding_requested": 750_000
        },
        corr,
        candidate["contract_id"],
        auth_decision="PROPOSAL_ONLY",
        required_authority="canonical_accounting"
    )
    underwriting = make_contract(
        "ProjectUnderwritingDecision",
        endpoint("Shtenco/synergy_financial_os", "underwriting", "canonical_accounting"),
        endpoint("Shtenco/synergy_eurasian", "project-model", "productive_project_model"),
        {
            "project_id": project["payload"]["project_id"],
            "decision": "CONDITIONAL",
            "approved_capacity": 500_000,
            "required_reserves": 100_000,
            "conditions": ["milestone-based-drawdown"],
            "underwriting_snapshot_ref": "snapshot:underwriting:001"
        },
        corr,
        project["contract_id"],
        auth_decision="NOT_REQUIRED",
        required_authority="canonical_accounting"
    )
    for contract in [candidate, project, underwriting]:
        validator.validate(contract, "science_eurasian_financial_v1.json")
    validator.validate_chain([candidate, project, underwriting])


def test_budget_to_metapay_to_financial_chain():
    corr = str(uuid4())
    authorization = make_contract(
        "BudgetPaymentAuthorization",
        endpoint("Shtenco/blochain_budget", "treasury-gateway", "state_budget_traceability"),
        endpoint("Shtenco/synergy_pay_system", "execution-router", "payment_execution_settlement"),
        {
            "authorization_id": str(uuid4()),
            "budget_entity": "region:001",
            "contract_ref": "procurement:2026:77",
            "beneficiary": "supplier:42",
            "asset": "KZT",
            "amount": 10_000_000,
            "purpose": "Delivered infrastructure equipment",
            "delivery_evidence_refs": ["delivery:hash:01"],
            "appropriation_ref": "appropriation:2026:infra"
        },
        corr,
        auth_decision="APPROVED",
        required_authority="budget_payment_authority"
    )
    settlement = make_contract(
        "BudgetSettlementEvidence",
        endpoint("Shtenco/synergy_pay_system", "settlement", "payment_execution_settlement"),
        endpoint("Shtenco/synergy_financial_os", "public-sector-ledger", "canonical_accounting"),
        {
            "authorization_id": authorization["payload"]["authorization_id"],
            "status": "SETTLED",
            "asset": "KZT",
            "gross_amount": 10_000_000,
            "fees": 1_500,
            "net_amount": 9_998_500,
            "external_reference": "bank-settlement-777",
            "settled_at": "2026-09-06T10:01:00Z"
        },
        corr,
        authorization["contract_id"],
        auth_decision="NOT_REQUIRED",
        required_authority="payment_execution_settlement"
    )
    recognition = make_contract(
        "BudgetAccountingRecognition",
        endpoint("Shtenco/synergy_financial_os", "public-sector-ledger", "canonical_accounting"),
        endpoint("Shtenco/blochain_budget", "audit-view", "state_budget_traceability"),
        {
            "authorization_id": authorization["payload"]["authorization_id"],
            "settlement_contract_id": settlement["contract_id"],
            "ledger_entry_ref": "ledger:budget:0001",
            "recognition_status": "RECOGNIZED",
            "economic_classification": "capital-expenditure"
        },
        corr,
        settlement["contract_id"],
        auth_decision="NOT_REQUIRED",
        required_authority="canonical_accounting"
    )
    for contract in [authorization, settlement, recognition]:
        validator.validate(contract, "budget_metapay_financial_v1.json")
    validator.validate_chain([authorization, settlement, recognition])


def test_financial_to_blockchain_to_metachain_chain():
    corr = str(uuid4())
    artifact = make_contract(
        "FinancialCommitmentArtifact",
        endpoint("Shtenco/synergy_financial_os", "accounting-close", "canonical_accounting"),
        endpoint("Shtenco/synergy_ai_blockchain", "commitment-ingress", "pq_chain_trust"),
        {
            "close_id": str(uuid4()),
            "snapshot_hash": "a" * 64,
            "merkle_root": "b" * 64,
            "hardnav": 1_250_000.0,
            "liquid_nav": 900_000.0,
            "liabilities": 250_000.0,
            "accounting_period_end": "2026-09-06T10:00:00Z"
        },
        corr,
        auth_decision="NOT_REQUIRED",
        required_authority="canonical_accounting"
    )
    receipt = make_contract(
        "ChainCommitmentReceipt",
        endpoint("Shtenco/synergy_ai_blockchain", "commitment-core", "pq_chain_trust"),
        endpoint("Shtenco/synergy_metachain", "light-client", "cross_chain_trust"),
        {
            "close_id": artifact["payload"]["close_id"],
            "chain_id": "synergy-testnet",
            "block_height": 12345,
            "tx_hash": "0xabc123",
            "commitment_hash": artifact["payload"]["snapshot_hash"],
            "finality_status": "FINAL"
        },
        corr,
        artifact["contract_id"],
        auth_decision="NOT_REQUIRED",
        required_authority="pq_chain_trust"
    )
    proof = make_contract(
        "MetaChainCheckpointProof",
        endpoint("Shtenco/synergy_metachain", "light-client", "cross_chain_trust"),
        endpoint("Shtenco/synergy_system", "evidence-registry", "architecture_governance"),
        {
            "source_chain_id": "synergy-testnet",
            "source_block_height": 12345,
            "source_commitment_hash": receipt["payload"]["commitment_hash"],
            "verification_method": "LIGHT_CLIENT",
            "verification_status": "VERIFIED",
            "proof_ref": "proof:checkpoint:12345",
            "security_assumptions": ["testnet-finality"]
        },
        corr,
        receipt["contract_id"],
        auth_decision="NOT_REQUIRED",
        required_authority="cross_chain_trust"
    )
    for contract in [artifact, receipt, proof]:
        validator.validate(contract, "financial_blockchain_metachain_v1.json")
    validator.validate_chain([artifact, receipt, proof])


def test_payload_tampering_is_rejected():
    corr = str(uuid4())
    contract = make_contract(
        "NexusPolicyProposal",
        endpoint("Shtenco/agi_nexus", "reasoner", "reasoning_core"),
        endpoint("Shtenco/agi_autopilot", "policy-engine", "action_orchestration"),
        {
            "proposal_id": str(uuid4()),
            "domain": "test",
            "objective": "x",
            "recommended_action": "y",
            "confidence": 0.5,
            "constraints": [],
            "risk_flags": [],
            "expires_at": None
        },
        corr,
        auth_decision="PROPOSAL_ONLY"
    )
    tampered = deepcopy(contract)
    tampered["payload"]["confidence"] = 0.99
    with pytest.raises(ContractValidationError, match="payload_hash"):
        validator.validate(tampered, "nexus_autopilot_v1.json")


def test_nexus_cannot_self_approve_execution():
    corr = str(uuid4())
    contract = make_contract(
        "NexusPolicyProposal",
        endpoint("Shtenco/agi_nexus", "reasoner", "reasoning_core"),
        endpoint("Shtenco/agi_autopilot", "policy-engine", "action_orchestration"),
        {
            "proposal_id": str(uuid4()),
            "domain": "finance",
            "objective": "execute",
            "recommended_action": "trade",
            "confidence": 0.9,
            "constraints": [],
            "risk_flags": [],
            "expires_at": None
        },
        corr,
        auth_decision="APPROVED"
    )
    with pytest.raises(ContractValidationError, match="NEXUS cannot grant"):
        validator.validate(contract, "nexus_autopilot_v1.json")
