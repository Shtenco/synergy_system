from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any


class EventEnvelopeError(ValueError):
    pass


@dataclass(frozen=True)
class SignatureBinding:
    algorithm: str
    key_id: str
    signer_repo: str
    signed_at: str
    signature: str

    def __post_init__(self) -> None:
        if not self.algorithm or not self.key_id or not self.signer_repo or not self.signature:
            raise EventEnvelopeError("signature binding is incomplete")


@dataclass(frozen=True)
class SecureEventEnvelope:
    """Immutable transport wrapper around a previously validated Federation contract.

    Delivery metadata is deliberately kept out of this object. Retries must never mutate
    the signed event or the underlying domain contract.
    """

    event_id: str
    event_version: int
    contract_id: str
    contract_type: str
    contract_version: int
    contract_payload_hash: str
    producer_repo: str
    producer_authority: str
    consumer_repo: str
    consumer_authority: str
    correlation_id: str
    causation_id: str | None
    validation_receipt_ref: str
    topic: str
    created_at: str
    signature: SignatureBinding | None = None

    def __post_init__(self) -> None:
        if self.event_version != 1:
            raise EventEnvelopeError("unsupported secure event version")
        required = {
            "event_id": self.event_id,
            "contract_id": self.contract_id,
            "contract_type": self.contract_type,
            "contract_payload_hash": self.contract_payload_hash,
            "producer_repo": self.producer_repo,
            "producer_authority": self.producer_authority,
            "consumer_repo": self.consumer_repo,
            "consumer_authority": self.consumer_authority,
            "correlation_id": self.correlation_id,
            "validation_receipt_ref": self.validation_receipt_ref,
            "topic": self.topic,
            "created_at": self.created_at,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise EventEnvelopeError(f"missing event fields: {', '.join(sorted(missing))}")
        if len(self.contract_payload_hash) != 64:
            raise EventEnvelopeError("contract_payload_hash must be a sha256 hex digest")

    def unsigned_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("signature", None)
        return data

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def with_signature(self, signature: SignatureBinding) -> "SecureEventEnvelope":
        return replace(self, signature=signature)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "SecureEventEnvelope":
        data = dict(value)
        signature = data.get("signature")
        if signature is not None and not isinstance(signature, SignatureBinding):
            data["signature"] = SignatureBinding(**signature)
        return cls(**data)
