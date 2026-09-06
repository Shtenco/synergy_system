from datetime import datetime, timedelta, timezone

import pytest

from synergy_data_fabric import ArchiveManifest, OfflinePayloadManifest, sha256_hex


def test_codec_change_does_not_change_semantic_digest():
    canonical = b'{"hardnav":"1000.00","status":"CLOSED"}'
    archive_a = b"SGH1\x00compressed-a"
    archive_b = b"zstd\x00compressed-b"

    a = ArchiveManifest.bind_lossless_archive(
        object_id="close-2026-09-06-001",
        object_class="ACCOUNTING_CLOSE",
        producer_repo="Shtenco/synergy_financial_os",
        semantic_owner_repo="Shtenco/synergy_financial_os",
        canonical_bytes=canonical,
        archive_bytes=archive_a,
        codec_id="GabrielHorn-SGH1",
        codec_version="1",
        storage_tier="COLD_IMMUTABLE_ARCHIVE",
    )
    b = ArchiveManifest.bind_lossless_archive(
        object_id="close-2026-09-06-001-reencoded",
        object_class="ACCOUNTING_CLOSE",
        producer_repo="Shtenco/synergy_financial_os",
        semantic_owner_repo="Shtenco/synergy_financial_os",
        canonical_bytes=canonical,
        archive_bytes=archive_b,
        codec_id="zstd",
        codec_version="19",
        storage_tier="COLD_IMMUTABLE_ARCHIVE",
    )

    assert a.canonical_content_sha256 == b.canonical_content_sha256
    assert a.archive_sha256 != b.archive_sha256
    assert a.verify_round_trip(canonical)
    assert b.verify_round_trip(canonical)


def test_tampered_archive_detected_independently_of_semantic_digest():
    canonical = b"scientific reproducibility package"
    archive = b"encoded-package"
    manifest = ArchiveManifest.bind_lossless_archive(
        object_id="science-repro-0001",
        object_class="SCIENCE_REPRO_PACKAGE",
        producer_repo="Shtenco/nexus_science_agent",
        semantic_owner_repo="Shtenco/nexus_science_agent",
        canonical_bytes=canonical,
        archive_bytes=archive,
        codec_id="GRAAL-IGC",
        codec_version="5.2",
        storage_tier="DISTRIBUTED_SYNERGYNET",
    )
    assert manifest.verify_archive_bytes(archive)
    assert not manifest.verify_archive_bytes(archive + b"tamper")
    assert manifest.canonical_content_sha256 == sha256_hex(canonical)


def test_raw_secret_material_rejected():
    digest = "a" * 64
    with pytest.raises(ValueError, match="raw secret material"):
        ArchiveManifest(
            object_id="secret-test-0001",
            object_class="USER_BACKUP_PACKAGE",
            producer_repo="Shtenco/synergy_app",
            semantic_owner_repo="Shtenco/synergy_app",
            canonical_content_sha256=digest,
            archive_sha256="b" * 64,
            codec_id="raw",
            codec_version="1",
            original_size=1,
            archive_size=1,
            storage_tier="HOT_LOCAL",
            created_at="2026-09-06T12:00:00+00:00",
            encrypted=True,
            encryption_algorithm="AES-256-GCM",
            key_reference="PRIVATE_KEY=deadbeef",
        )


def test_qtc2_shared_model_binding_and_no_authority():
    now = datetime.now(timezone.utc)
    manifest = OfflinePayloadManifest(
        payload_id="offline-payment-ref-0001",
        payload_type="PAYMENT_INTENT_REFERENCE",
        issuer_repo="Shtenco/synergy_pay_system",
        target_repo="Shtenco/synergy_pay_system",
        canonical_content_sha256="c" * 64,
        encoding_profile="QTC2_PATCH",
        shared_model_sha256="d" * 64,
        temporal_slot=123456,
        created_at=now.isoformat(),
        expires_at=(now + timedelta(minutes=10)).isoformat(),
        replay_nonce="nonce-1234567890abcdef",
        signature_algorithm="ML-DSA-65",
        signing_key_reference="kms://synergy/metapay/offline-signing-v1",
        authorization_conferred=False,
    )
    assert manifest.authorization_conferred is False
    assert not manifest.is_expired(now)


def test_qtc2_without_model_is_rejected():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="shared model"):
        OfflinePayloadManifest(
            payload_id="offline-proof-ref-0001",
            payload_type="PUBLIC_BUDGET_PROOF_REFERENCE",
            issuer_repo="Shtenco/blochain_budget",
            target_repo="Shtenco/blochain_budget",
            canonical_content_sha256="e" * 64,
            encoding_profile="QTC2_EXACT",
            created_at=now.isoformat(),
            expires_at=(now + timedelta(hours=1)).isoformat(),
            replay_nonce="nonce-abcdef1234567890",
            signature_algorithm="ML-DSA-65",
            signing_key_reference="kms://synergy/budget/offline-v1",
        )


def test_offline_payload_can_never_confer_authority():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="never confers authorization"):
        OfflinePayloadManifest(
            payload_id="offline-node-ref-0001",
            payload_type="NODE_ENROLLMENT_REFERENCE",
            issuer_repo="Shtenco/synergy_meta_os",
            target_repo="Shtenco/synergy_meta_os",
            canonical_content_sha256="f" * 64,
            encoding_profile="QTC2_STANDALONE",
            created_at=now.isoformat(),
            expires_at=(now + timedelta(minutes=5)).isoformat(),
            replay_nonce="nonce-0011223344556677",
            signature_algorithm="ML-DSA-65",
            signing_key_reference="kms://synergy/meta-os/enrollment-v1",
            authorization_conferred=True,
        )
