from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

import pytest

from synergy_event_fabric import (
    CompensationMode,
    CompensationReceipt,
    CompensationRequest,
    CompensationStatus,
    DurableEventStore,
    EventConsumer,
    EventEnvelopeError,
    EventPublisher,
    HmacSha256DevProvider,
    OutboxDispatcher,
    SignaturePolicy,
    build_event,
    sign_event,
    verify_event_signature,
)
from synergy_contracts.validation import canonical_payload_hash


NOW = "2026-09-06T10:30:00Z"


def endpoint(repo: str, component: str, authority: str) -> dict:
    return {"repo": repo, "component": component, "authority": authority}


def trading_intent() -> dict:
    payload = {
        "strategy_id": "MIDAS-V32.1",
        "instrument": "EURUSD",
        "side": "BUY",
        "quantity": 100000,
        "max_total_cost": 45.0,
        "settlement_date": "2026-09-08",
        "venue_constraints": ["prefunded"],
        "risk_budget_ref": "risk:test",
        "expected_edge_bps": 4.2,
    }
    return {
        "schema_id": "synergy.contract-envelope/v1",
        "contract_type": "TradingExecutionIntent",
        "contract_version": 1,
        "contract_id": str(uuid4()),
        "created_at": NOW,
        "producer": endpoint("Shtenco/midas_ai", "portfolio-executor", "trading_intelligence"),
        "consumer": endpoint("Shtenco/synergy_pay_system", "execution-router", "payment_execution_settlement"),
        "correlation_id": str(uuid4()),
        "causation_id": None,
        "provenance": {"code_commit": "abcdef1", "model_id": None, "data_cutoff": NOW, "epistemic_state": "KNOWN", "source_refs": ["test"]},
        "authorization": {"required_authority": "trading_execution", "decision": "APPROVED", "granted_by": "test", "grant_ref": "grant:test"},
        "evidence": {"hash_alg": "sha256", "payload_hash": canonical_payload_hash(payload), "refs": ["test"]},
        "payload": payload,
    }


def signer() -> HmacSha256DevProvider:
    return HmacSha256DevProvider(
        secret=b"0123456789abcdef0123456789abcdef",
        key_id="midas-test-key",
        signer_repo="Shtenco/midas_ai",
    )


def dev_policy() -> SignaturePolicy:
    return SignaturePolicy(require_pq=False, allow_dev_algorithms=True)


def test_signature_binds_route_and_contract_hash():
    event = build_event(trading_intent(), "validation:test:1", NOW)
    signed = sign_event(event, signer(), NOW)
    verify_event_signature(signed, signer(), dev_policy())

    tampered = replace(signed, topic=signed.topic + ".evil")
    with pytest.raises(EventEnvelopeError, match="verification failed"):
        verify_event_signature(tampered, signer(), dev_policy())


def test_dev_signature_is_rejected_by_production_pq_policy():
    signed = sign_event(build_event(trading_intent(), "validation:test:2", NOW), signer(), NOW)
    with pytest.raises(EventEnvelopeError, match="non-PQ"):
        verify_event_signature(signed, signer(), SignaturePolicy(require_pq=True, allow_dev_algorithms=False))


def test_outbox_and_replay_ledger_survive_restart(tmp_path):
    db = tmp_path / "fabric.db"
    contract = trading_intent()

    store = DurableEventStore(db)
    published = EventPublisher(store, signer()).publish(contract, "validation:test:3", NOW)
    assert store.outbox_state(published.event_id) == "PENDING"
    store.close()

    store = DurableEventStore(db)
    assert store.outbox_state(published.event_id) == "PENDING"
    consumer = EventConsumer(
        store,
        "Shtenco/synergy_pay_system",
        provider_resolver=lambda _event: signer(),
        signature_policy=dev_policy(),
    )
    assert consumer.ingest(published, NOW) == "ACCEPTED"
    assert consumer.ingest(published, NOW) == "DUPLICATE"
    store.close()

    store = DurableEventStore(db)
    consumer = EventConsumer(
        store,
        "Shtenco/synergy_pay_system",
        provider_resolver=lambda _event: signer(),
        signature_policy=dev_policy(),
    )
    assert consumer.ingest(published, NOW) == "DUPLICATE"
    assert store.count("replay_ledger") == 1
    assert store.count("event_inbox") == 1
    store.close()


def test_dispatch_retry_exhaustion_moves_event_to_dlq(tmp_path):
    store = DurableEventStore(tmp_path / "retry.db")
    event = EventPublisher(store, signer()).publish(trading_intent(), "validation:test:4", "2026-09-06T10:00:00Z")

    def broken_transport(_event):
        raise ConnectionError("SynergyNet path unavailable")

    dispatcher = OutboxDispatcher(store, broken_transport, max_attempts=2, base_backoff_seconds=1)
    first = dispatcher.dispatch_once("2026-09-06T10:00:00Z")
    assert first == {"claimed": 1, "delivered": 0, "retry": 1, "dead": 0}
    assert store.outbox_state(event.event_id) == "RETRY"

    second = dispatcher.dispatch_once("2026-09-06T10:00:01Z")
    assert second == {"claimed": 1, "delivered": 0, "retry": 0, "dead": 1}
    assert store.outbox_state(event.event_id) == "DEAD"
    assert store.count("dead_letter") == 1
    assert store.count("delivery_attempts") == 2
    store.close()


def test_invalid_signature_is_quarantined(tmp_path):
    store = DurableEventStore(tmp_path / "quarantine.db")
    signed = sign_event(build_event(trading_intent(), "validation:test:5", NOW), signer(), NOW)
    tampered = replace(signed, consumer_authority="forged-authority")
    consumer = EventConsumer(
        store,
        "Shtenco/synergy_pay_system",
        provider_resolver=lambda _event: signer(),
        signature_policy=dev_policy(),
    )
    with pytest.raises(EventEnvelopeError):
        consumer.ingest(tampered, NOW)
    assert store.count("quarantine") == 1
    assert store.count("event_inbox") == 0
    store.close()


def test_compensation_never_overwrites_original_contract():
    original_id = str(uuid4())
    request = CompensationRequest(
        request_id=str(uuid4()),
        original_contract_id=original_id,
        correlation_id=str(uuid4()),
        requested_by_repo="Shtenco/synergy_pay_system",
        requested_by_authority="payment_execution_settlement",
        mode=CompensationMode.REVERSAL,
        reason="external settlement was reversed",
        requested_at=NOW,
    )
    receipt = CompensationReceipt(
        request_id=request.request_id,
        original_contract_id=original_id,
        compensation_contract_id=str(uuid4()),
        status=CompensationStatus.APPLIED,
        decided_by_repo="Shtenco/synergy_financial_os",
        decided_by_authority="canonical_accounting",
        decided_at=NOW,
        evidence_refs=("settlement:reversal:1",),
    )
    assert receipt.compensation_contract_id != receipt.original_contract_id

    with pytest.raises(ValueError, match="never overwrite"):
        CompensationReceipt(
            request_id=request.request_id,
            original_contract_id=original_id,
            compensation_contract_id=original_id,
            status=CompensationStatus.APPLIED,
            decided_by_repo="Shtenco/synergy_financial_os",
            decided_by_authority="canonical_accounting",
            decided_at=NOW,
            evidence_refs=(),
        )
