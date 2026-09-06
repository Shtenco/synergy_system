from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Callable
from uuid import uuid4

from .crypto import SignaturePolicy, SignatureProvider, sign_event, verify_event_signature
from .model import EventEnvelopeError, SecureEventEnvelope
from .store import DurableEventStore


class FabricRuntimeError(RuntimeError):
    pass


def topic_for_contract(contract: dict) -> str:
    consumer_repo = contract["consumer"]["repo"]
    repo_slug = consumer_repo.replace("Shtenco/", "").replace("_", "-")
    contract_type = contract["contract_type"]
    contract_slug = "".join(("-" + c.lower()) if c.isupper() else c for c in contract_type).lstrip("-")
    return f"synergy.contract.{repo_slug}.{contract_slug}.v1"


def build_event(
    contract: dict,
    validation_receipt_ref: str,
    created_at: str,
    event_id: str | None = None,
) -> SecureEventEnvelope:
    """Wrap a validated contract without copying/mutating domain payload data."""
    if not validation_receipt_ref:
        raise EventEnvelopeError("validation receipt is required before event publication")
    payload_hash = contract["evidence"]["payload_hash"]
    return SecureEventEnvelope(
        event_id=event_id or str(uuid4()),
        event_version=1,
        contract_id=contract["contract_id"],
        contract_type=contract["contract_type"],
        contract_version=int(contract["contract_version"]),
        contract_payload_hash=payload_hash,
        producer_repo=contract["producer"]["repo"],
        producer_authority=contract["producer"]["authority"],
        consumer_repo=contract["consumer"]["repo"],
        consumer_authority=contract["consumer"]["authority"],
        correlation_id=contract["correlation_id"],
        causation_id=contract.get("causation_id"),
        validation_receipt_ref=validation_receipt_ref,
        topic=topic_for_contract(contract),
        created_at=created_at,
    )


class EventPublisher:
    def __init__(self, store: DurableEventStore, signer: SignatureProvider):
        self.store = store
        self.signer = signer

    def publish(self, contract: dict, validation_receipt_ref: str, now: str) -> SecureEventEnvelope:
        event = build_event(contract, validation_receipt_ref, now)
        signed = sign_event(event, self.signer, signed_at=now)
        inserted = self.store.enqueue_outbox(signed, now=now)
        if not inserted:
            raise FabricRuntimeError("contract/topic is already present in durable outbox")
        return signed


class EventConsumer:
    def __init__(
        self,
        store: DurableEventStore,
        consumer_repo: str,
        provider_resolver: Callable[[SecureEventEnvelope], SignatureProvider],
        signature_policy: SignaturePolicy,
    ):
        self.store = store
        self.consumer_repo = consumer_repo
        self.provider_resolver = provider_resolver
        self.signature_policy = signature_policy

    def ingest(self, event: SecureEventEnvelope, now: str) -> str:
        try:
            provider = self.provider_resolver(event)
            verify_event_signature(event, provider, self.signature_policy)
            if event.consumer_repo != self.consumer_repo:
                raise EventEnvelopeError("event consumer does not match receiving node")
            inserted = self.store.receive_once(event, self.consumer_repo, now)
            return "ACCEPTED" if inserted else "DUPLICATE"
        except Exception as exc:
            self.store.quarantine_event(event, str(exc), now)
            raise

    def mark_processed(self, contract_id: str, now: str) -> None:
        self.store.mark_inbox_processed(self.consumer_repo, contract_id, now)


class OutboxDispatcher:
    """Reference dispatcher: durable claim -> SynergyNet send -> ack/retry/DLQ."""

    def __init__(
        self,
        store: DurableEventStore,
        send: Callable[[SecureEventEnvelope], None],
        max_attempts: int = 5,
        base_backoff_seconds: int = 1,
        max_backoff_seconds: int = 300,
    ):
        if max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        self.store = store
        self.send = send
        self.max_attempts = max_attempts
        self.base_backoff_seconds = base_backoff_seconds
        self.max_backoff_seconds = max_backoff_seconds

    @staticmethod
    def _parse_time(value: str) -> datetime:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed

    @staticmethod
    def _format_time(value: datetime) -> str:
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    def _retry_at(self, now: str, attempts: int) -> str:
        exponent = max(0, attempts - 1)
        delay = min(self.base_backoff_seconds * (2**exponent), self.max_backoff_seconds)
        return self._format_time(self._parse_time(now) + timedelta(seconds=delay))

    def dispatch_once(self, now: str, limit: int = 100) -> dict[str, int]:
        stats = {"claimed": 0, "delivered": 0, "retry": 0, "dead": 0}
        records = self.store.claim_ready(now=now, limit=limit)
        stats["claimed"] = len(records)
        for record in records:
            try:
                self.send(record.event)
            except Exception as exc:
                state = self.store.fail_attempt(
                    event_id=record.event.event_id,
                    error=f"{type(exc).__name__}: {exc}",
                    now=now,
                    retry_at=self._retry_at(now, record.attempts),
                    max_attempts=self.max_attempts,
                )
                stats["dead" if state == "DEAD" else "retry"] += 1
            else:
                self.store.mark_delivered(record.event.event_id, now=now)
                stats["delivered"] += 1
        return stats
