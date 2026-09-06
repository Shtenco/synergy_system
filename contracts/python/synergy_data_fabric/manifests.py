from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Iterable


def sha256_hex(data: bytes) -> str:
    return sha256(data).hexdigest()


def _require_sha256(value: str, field_name: str) -> None:
    if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise ValueError(f"{field_name} must be lowercase SHA-256 hex")


@dataclass(frozen=True)
class ArchiveManifest:
    object_id: str
    object_class: str
    producer_repo: str
    semantic_owner_repo: str
    canonical_content_sha256: str
    archive_sha256: str
    codec_id: str
    codec_version: str
    original_size: int
    archive_size: int
    storage_tier: str
    created_at: str
    dictionary_or_model_sha256: str | None = None
    chunk_sha256: tuple[str, ...] = field(default_factory=tuple)
    provenance_refs: tuple[str, ...] = field(default_factory=tuple)
    encrypted: bool = False
    encryption_algorithm: str | None = None
    key_reference: str | None = None
    retention_class: str = "STANDARD"
    schema: str = "synergy.archive-manifest/v1"

    def __post_init__(self) -> None:
        if self.original_size < 0 or self.archive_size < 0:
            raise ValueError("sizes cannot be negative")
        _require_sha256(self.canonical_content_sha256, "canonical_content_sha256")
        _require_sha256(self.archive_sha256, "archive_sha256")
        if self.dictionary_or_model_sha256 is not None:
            _require_sha256(self.dictionary_or_model_sha256, "dictionary_or_model_sha256")
        for digest in self.chunk_sha256:
            _require_sha256(digest, "chunk_sha256")
        if len(set(self.chunk_sha256)) != len(self.chunk_sha256):
            raise ValueError("chunk_sha256 entries must be unique")
        if self.encrypted and not self.key_reference:
            raise ValueError("encrypted archive requires external key_reference")
        if not self.encrypted and self.key_reference:
            raise ValueError("key_reference is invalid for an unencrypted archive")
        if self.key_reference and any(token in self.key_reference.upper() for token in ("PRIVATE_KEY=", "SEED=", "MNEMONIC=")):
            raise ValueError("raw secret material is forbidden; use an external key reference")

    @classmethod
    def bind_lossless_archive(
        cls,
        *,
        object_id: str,
        object_class: str,
        producer_repo: str,
        semantic_owner_repo: str,
        canonical_bytes: bytes,
        archive_bytes: bytes,
        codec_id: str,
        codec_version: str,
        storage_tier: str,
        dictionary_or_model_sha256: str | None = None,
        chunk_digests: Iterable[str] = (),
    ) -> "ArchiveManifest":
        return cls(
            object_id=object_id,
            object_class=object_class,
            producer_repo=producer_repo,
            semantic_owner_repo=semantic_owner_repo,
            canonical_content_sha256=sha256_hex(canonical_bytes),
            archive_sha256=sha256_hex(archive_bytes),
            codec_id=codec_id,
            codec_version=codec_version,
            original_size=len(canonical_bytes),
            archive_size=len(archive_bytes),
            storage_tier=storage_tier,
            created_at=datetime.now(timezone.utc).isoformat(),
            dictionary_or_model_sha256=dictionary_or_model_sha256,
            chunk_sha256=tuple(chunk_digests),
        )

    def verify_round_trip(self, decoded_canonical_bytes: bytes) -> bool:
        return sha256_hex(decoded_canonical_bytes) == self.canonical_content_sha256

    def verify_archive_bytes(self, archive_bytes: bytes) -> bool:
        return sha256_hex(archive_bytes) == self.archive_sha256


@dataclass(frozen=True)
class OfflinePayloadManifest:
    payload_id: str
    payload_type: str
    issuer_repo: str
    target_repo: str
    canonical_content_sha256: str
    encoding_profile: str
    created_at: str
    expires_at: str
    replay_nonce: str
    signature_algorithm: str
    signing_key_reference: str
    authorization_conferred: bool = False
    shared_model_sha256: str | None = None
    temporal_slot: int | None = None
    frame_set_sha256: str | None = None
    schema: str = "synergy.offline-payload-manifest/v1"

    def __post_init__(self) -> None:
        _require_sha256(self.canonical_content_sha256, "canonical_content_sha256")
        if self.authorization_conferred:
            raise ValueError("offline/QR transport never confers authorization")
        if len(self.replay_nonce) < 16:
            raise ValueError("replay_nonce must have at least 16 characters")
        if self.shared_model_sha256 is not None:
            _require_sha256(self.shared_model_sha256, "shared_model_sha256")
        if self.frame_set_sha256 is not None:
            _require_sha256(self.frame_set_sha256, "frame_set_sha256")
        if self.encoding_profile in {"QTC2_EXACT", "QTC2_PATCH"}:
            if self.shared_model_sha256 is None or self.temporal_slot is None:
                raise ValueError("QTC2 exact/patch requires shared model digest and temporal slot")
        created = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
        expires = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
        if expires <= created:
            raise ValueError("expires_at must be after created_at")

    def is_expired(self, now: datetime | None = None) -> bool:
        current = now or datetime.now(timezone.utc)
        expiry = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        return current >= expiry
