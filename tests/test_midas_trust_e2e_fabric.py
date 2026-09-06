from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from synergy_contracts.validation import ContractValidator, canonical_payload_hash
from synergy_event_fabric import (
    DurableEventStore,
    EventConsumer,
    EventPublisher,
    HmacSha256DevProvider,
    OutboxDispatcher,
    SignaturePolicy,
)


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ContractValidator(ROOT / "schemas")
NOW = "2026-09-06T10:40:00Z"


def endpoint(repo: str, component: str, authority: str) -> dict:
    return {"repo": repo, "component": component, "authority": authority}


def contract(
    contract_type: str,
    producer: dict,
    consumer: dict,
    payload: dict,
    correlation_id: str,
    causation_id: str | None,
    auth_decision: str = "NOT_REQUIRED",
    required_authority: str = "domain_authority",
) -> dict:
    payload_hash = canonical_payload_hash(payload)
    return {
        "schema_id": "synergy.contract-envelope/v1",
        "contract_type": contract_type,
        "contract_version": 1,
        "contract_id": str(uuid4()),
        "created_at": NOW,
        "producer": producer,
        "consumer": consumer,
        "correlation_id": correlation_id,
        "causation_id": causation_id,
        "provenance": {
            "code_commit": "abcdef1",
            "model_id": None,
            "data_cutoff": NOW,
            "epistemic_state": "KNOWN",
            "source_refs": ["e2e:test"],
        },
        "authorization": {
            "required_authority": required_authority,
            "decision": auth_decision,
            "granted_by": "e2e-authority" if auth_decision == "APPROVED" else None,
            "grant_ref": "e2e:grant" if auth_decision == "APPROVED" else None,
        },
        "evidence": {"hash_alg": "sha256", "payload_hash": payload_hash, "refs": ["e2e:test"]},
        "payload": payload,
    }


def build_chain() -> list[tuple[dict, str]]:
    corr = str(uuid4())
    intent = contract(
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
            "risk_budget_ref": "risk:e2e:fx",
            "expected_edge_bps": 4.2,
        },
        corr,
        None,
        auth_decision="APPROVED",
        required_authority="trading_execution",
    )
    settlement = contract(
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
            "external_reference": "broker-fill-e2e-001",
            "settled_at": "2026-09-06T10:40:02Z",
            "counterparty": "broker",
        },
        corr,
        intent["contract_id"],
        required_authority="payment_execution_settlement",
    )
    result = contract(
        "ReconciledTradingResult",
        endpoint("Shtenco/synergy_financial_os", "reconciliation", "canonical_accounting"),
        endpoint("Shtenco/midas_ai", "performance-ledger", "trading_intelligence"),
        {
            "execution_intent_id": intent["contract_id"],
            "settlement_contract_id": settlement["contract_id"],
            "realized_pnl": 400.0,
            "hardnav_delta": 400.0,
            "reconciliation_status": "MATCHED",
        },
        corr,
        settlement["contract_id"],
        required_authority="canonical_accounting",
    )
    close_id = str(uuid4())
    snapshot_hash = "a" * 64
    artifact = contract(
        "FinancialCommitmentArtifact",
        endpoint("Shtenco/synergy_financial_os", "accounting-close", "canonical_accounting"),
        endpoint("Shtenco/synergy_ai_blockchain", "commitment-ingress", "pq_chain_trust"),
        {
            "close_id": close_id,
            "snapshot_hash": snapshot_hash,
            "merkle_root": "b" * 64,
            "hardnav": 1_250_400.0,
            "liquid_nav": 900_400.0,
            "liabilities": 250_000.0,
            "accounting_period_end": "2026-09-06T10:40:03Z",
        },
        corr,
        result["contract_id"],
        required_authority="canonical_accounting",
    )
    receipt = contract(
        "ChainCommitmentReceipt",
        endpoint("Shtenco/synergy_ai_blockchain", "commitment-core", "pq_chain_trust"),
        endpoint("Shtenco/synergy_metachain", "light-client", "cross_chain_trust"),
        {
            "close_id": close_id,
            "chain_id": "synergy-testnet",
            "block_height": 12345,
            "tx_hash": "0xe2e123",
            "commitment_hash": snapshot_hash,
            "finality_status": "FINAL",
        },
        corr,
        artifact["contract_id"],
        required_authority="pq_chain_trust",
    )
    proof = contract(
        "MetaChainCheckpointProof",
        endpoint("Shtenco/synergy_metachain", "light-client", "cross_chain_trust"),
        endpoint("Shtenco/synergy_system", "evidence-registry", "architecture_governance"),
        {
            "source_chain_id": "synergy-testnet",
            "source_block_height": 12345,
            "source_commitment_hash": snapshot_hash,
            "verification_method": "LIGHT_CLIENT",
            "verification_status": "VERIFIED",
            "proof_ref": "proof:e2e:12345",
            "security_assumptions": ["testnet-finality"],
        },
        corr,
        receipt["contract_id"],
        required_authority="cross_chain_trust",
    )
    return [
        (intent, "midas_metapay_financial_v1.json"),
        (settlement, "midas_metapay_financial_v1.json"),
        (result, "midas_metapay_financial_v1.json"),
        (artifact, "financial_blockchain_metachain_v1.json"),
        (receipt, "financial_blockchain_metachain_v1.json"),
        (proof, "financial_blockchain_metachain_v1.json"),
    ]


def signer_for(repo: str) -> HmacSha256DevProvider:
    key_material = (repo + "|secure-event-fabric-e2e").encode("utf-8")
    secret = (key_material * ((32 // len(key_material)) + 2))[:32]
    return HmacSha256DevProvider(secret=secret, key_id=f"{repo}:test-key", signer_repo=repo)


def test_midas_to_metachain_durable_signed_e2e(tmp_path):
    chain_with_schemas = build_chain()
    chain = [item[0] for item in chain_with_schemas]
    for item, schema in chain_with_schemas:
        VALIDATOR.validate(item, schema)
    VALIDATOR.validate_chain(chain)

    repos = {
        "Shtenco/midas_ai",
        "Shtenco/synergy_pay_system",
        "Shtenco/synergy_financial_os",
        "Shtenco/synergy_ai_blockchain",
        "Shtenco/synergy_metachain",
        "Shtenco/synergy_system",
    }
    stores = {repo: DurableEventStore(tmp_path / (repo.split("/")[-1] + ".db")) for repo in repos}
    signers = {repo: signer_for(repo) for repo in repos}
    policy = SignaturePolicy(require_pq=False, allow_dev_algorithms=True)
    consumers = {
        repo: EventConsumer(
            stores[repo],
            repo,
            provider_resolver=lambda event, mapping=signers: mapping[event.producer_repo],
            signature_policy=policy,
        )
        for repo in repos
    }

    delivered_events = []
    for index, item in enumerate(chain):
        producer_repo = item["producer"]["repo"]
        publisher = EventPublisher(stores[producer_repo], signers[producer_repo])
        event = publisher.publish(item, f"validation:e2e:{index}", NOW)
        delivered_events.append(event)

        def send(evt):
            target = consumers[evt.consumer_repo]
            status = target.ingest(evt, NOW)
            if status == "ACCEPTED":
                target.mark_processed(evt.contract_id, NOW)

        stats = OutboxDispatcher(stores[producer_repo], send, max_attempts=3).dispatch_once(NOW)
        assert stats["delivered"] == 1
        assert stores[producer_repo].outbox_state(event.event_id) == "DELIVERED"
        assert stores[item["consumer"]["repo"]].inbox_status(item["consumer"]["repo"], item["contract_id"]) == "PROCESSED"

    # Re-delivery is harmless: consumer idempotency is keyed by immutable contract_id.
    final_event = delivered_events[-1]
    assert consumers[final_event.consumer_repo].ingest(final_event, NOW) == "DUPLICATE"

    assert chain[1]["payload"]["status"] == "SETTLED"
    assert chain[2]["payload"]["realized_pnl"] == chain[2]["payload"]["hardnav_delta"] == 400.0
    assert chain[3]["payload"]["snapshot_hash"] == chain[4]["payload"]["commitment_hash"]
    assert chain[4]["payload"]["commitment_hash"] == chain[5]["payload"]["source_commitment_hash"]
    assert chain[5]["payload"]["verification_status"] == "VERIFIED"

    for store in stores.values():
        store.close()
