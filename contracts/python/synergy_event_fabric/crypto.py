from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Protocol

from .model import EventEnvelopeError, SecureEventEnvelope, SignatureBinding


PQ_ALGORITHMS = frozenset({
    "ML-DSA-44",
    "ML-DSA-65",
    "ML-DSA-87",
    "SLH-DSA-SHA2-128S",
    "SLH-DSA-SHA2-192S",
    "SLH-DSA-SHA2-256S",
})
DEV_ALGORITHMS = frozenset({"HMAC-SHA256-DEV"})


class SignatureProvider(Protocol):
    algorithm: str
    key_id: str
    signer_repo: str

    def sign(self, message: bytes) -> str: ...

    def verify(self, message: bytes, signature: str) -> bool: ...


@dataclass(frozen=True)
class SignaturePolicy:
    require_pq: bool = True
    allow_dev_algorithms: bool = False

    def validate_algorithm(self, algorithm: str) -> None:
        if algorithm in PQ_ALGORITHMS:
            return
        if self.allow_dev_algorithms and algorithm in DEV_ALGORITHMS:
            return
        if self.require_pq:
            raise EventEnvelopeError(f"non-PQ event signature rejected: {algorithm}")
        raise EventEnvelopeError(f"signature algorithm not allowed: {algorithm}")


def canonical_event_bytes(event: SecureEventEnvelope) -> bytes:
    return json.dumps(
        event.unsigned_dict(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


class HmacSha256DevProvider:
    """Test-only signer.

    This is intentionally named DEV and must never satisfy a production PQ policy.
    It gives deterministic cryptographic binding for contract/event tests without
    pretending that a post-quantum provider is already deployed.
    """

    algorithm = "HMAC-SHA256-DEV"

    def __init__(self, secret: bytes, key_id: str, signer_repo: str):
        if len(secret) < 16:
            raise ValueError("development HMAC secret must be at least 16 bytes")
        self._secret = secret
        self.key_id = key_id
        self.signer_repo = signer_repo

    def sign(self, message: bytes) -> str:
        return hmac.new(self._secret, message, hashlib.sha256).hexdigest()

    def verify(self, message: bytes, signature: str) -> bool:
        expected = self.sign(message)
        return hmac.compare_digest(expected, signature)


def sign_event(event: SecureEventEnvelope, provider: SignatureProvider, signed_at: str) -> SecureEventEnvelope:
    if event.signature is not None:
        raise EventEnvelopeError("event is already signed")
    if provider.signer_repo != event.producer_repo:
        raise EventEnvelopeError("signature provider does not belong to event producer")
    signature = provider.sign(canonical_event_bytes(event))
    return event.with_signature(
        SignatureBinding(
            algorithm=provider.algorithm,
            key_id=provider.key_id,
            signer_repo=provider.signer_repo,
            signed_at=signed_at,
            signature=signature,
        )
    )


def verify_event_signature(
    event: SecureEventEnvelope,
    provider: SignatureProvider,
    policy: SignaturePolicy,
) -> None:
    binding = event.signature
    if binding is None:
        raise EventEnvelopeError("unsigned secure event")
    policy.validate_algorithm(binding.algorithm)
    if binding.algorithm != provider.algorithm:
        raise EventEnvelopeError("signature algorithm/provider mismatch")
    if binding.key_id != provider.key_id:
        raise EventEnvelopeError("signature key id/provider mismatch")
    if binding.signer_repo != event.producer_repo or binding.signer_repo != provider.signer_repo:
        raise EventEnvelopeError("signature signer does not match producer authority boundary")
    if not provider.verify(canonical_event_bytes(event), binding.signature):
        raise EventEnvelopeError("event signature verification failed")


class PqSignatureProvider(Protocol):
    """Binding contract for real ML-DSA/SLH-DSA providers.

    Concrete production implementations live with the trust/key-management layer.
    Secure Event Fabric consumes this interface and does not embed private keys.
    """

    algorithm: str
    key_id: str
    signer_repo: str

    def sign(self, message: bytes) -> str: ...
    def verify(self, message: bytes, signature: str) -> bool: ...
