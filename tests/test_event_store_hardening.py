from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

import pytest

from synergy_contracts.validation import canonical_payload_hash
from synergy_event_fabric import DurableEventStore, HmacSha256DevProvider, build_event, sign_event


T0 = "2026-09-06T10:00:00Z"


def endpoint(repo: str, component: str, authority: str) -> dict:
    return {"repo": repo, "component": component, "authority": authority}


def contract() -> dict:
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
        "created_at": T0,
        "producer": endpoint("Shtenco/midas_ai", "portfolio-executor", "trading_intelligence"),
        "consumer": endpoint("Shtenco/synergy_pay_system", "execution-router", "payment_execution_settlement"),
        "correlation_id": str(uuid4()),
        "causation_id": None,
        "provenance": {"code_commit": "abcdef1", "model_id": None, "data_cutoff": T0, "epistemic_state": "KNOWN", "source_refs": ["test"]},
        "authorization": {"required_authority": "trading_execution", "decision": "APPROVED", "granted_by": "test", "grant_ref": "test"},
        "evidence": {"hash_alg": "sha256", "payload_hash": canonical_payload_hash(payload), "refs": ["test"]},
        "payload": payload,
    }


def signed_event(item: dict):
    signer = HmacSha256DevProvider(b"0123456789abcdef0123456789abcdef", "test", "Shtenco/midas_ai")
    return sign_event(build_event(item, "validation:test", T0), signer, T0)


def test_stale_inflight_lease_is_recovered_after_worker_crash(tmp_path):
    store = DurableEventStore(tmp_path / "lease.db")
    event = signed_event(contract())
    assert store.enqueue_outbox(event, T0)
    claimed = store.claim_ready(T0, lease_seconds=1)
    assert len(claimed) == 1
    assert store.outbox_state(event.event_id) == "INFLIGHT"

    recovered = store.recover_stale_inflight("2026-09-06T10:00:01Z")
    assert recovered == 1
    assert store.outbox_state(event.event_id) == "RETRY"

    claimed_again = store.claim_ready("2026-09-06T10:00:01Z", lease_seconds=1)
    assert len(claimed_again) == 1
    assert claimed_again[0].attempts == 2
    store.close()


def test_same_contract_id_with_different_hash_is_not_a_duplicate(tmp_path):
    store = DurableEventStore(tmp_path / "replay.db")
    item = contract()
    first = signed_event(item)
    assert store.receive_once(first, first.consumer_repo, T0)

    conflicting = replace(first, contract_payload_hash="f" * 64)
    with pytest.raises(ValueError, match="conflicting payload hash"):
        store.receive_once(conflicting, conflicting.consumer_repo, T0)
    store.close()


def test_outbox_same_contract_id_cannot_be_retargeted(tmp_path):
    store = DurableEventStore(tmp_path / "outbox-conflict.db")
    event = signed_event(contract())
    assert store.enqueue_outbox(event, T0)
    retargeted = replace(event, topic=event.topic + ".forged")
    with pytest.raises(ValueError, match="conflicting topic"):
        store.enqueue_outbox(retargeted, T0)
    store.close()
