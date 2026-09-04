from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any, Mapping

SCHEMA = "synergy.artifact-evidence-envelope/v1"
EVIDENCE_STATUS = "PROVENANCE_ENVELOPE_ONLY"
AUTHORITY_SCOPE = "IDENTITY_AND_PROVENANCE_ONLY"
HEX40 = frozenset("0123456789abcdef")
HEX64 = HEX40

TOP_LEVEL_FIELDS = frozenset(
    {
        "schema",
        "envelope_id",
        "artifact_type",
        "artifact_schema",
        "artifact_digest",
        "source_repository",
        "source_commit",
        "producer_repository",
        "authority_domain",
        "authority_scope",
        "environment",
        "evidence_status",
        "source_status_text",
        "source_verifier_digest",
        "observed_at",
        "parent_digests",
        "metadata",
        "financial_authority",
        "payment_authority",
        "accounting_authority",
        "execution_authority",
        "signing_authority",
        "blockchain_submission_authority",
        "production_deployment_authority",
        "merge_authority",
        "envelope_digest",
    }
)
METADATA_FIELDS = frozenset(
    {"artifact_path", "content_media_type", "human_label"}
)
AUTHORITY_DOMAINS = frozenset(
    {
        "ARCHITECTURE_GOVERNANCE",
        "FINANCIAL_ACCOUNTING",
        "SETTLEMENT",
        "TRUST_COMMITMENT",
        "NETWORK_TRANSPORT",
        "RUNTIME_ORCHESTRATION",
        "HOST_EXECUTION",
        "AI_INFERENCE",
        "AI_PROPOSAL",
        "TRADING_PROPOSAL",
        "ENGINEERING_TRACE",
        "COMPRESSION_IDENTITY",
        "SCIENTIFIC_RESEARCH",
        "PUBLIC_TRACE_EVIDENCE",
        "DOMAIN_EVIDENCE",
        "CLIENT_PRESENTATION",
        "PRESENTATION_ONLY",
        "RESEARCH_ONLY",
        "NONE",
    }
)
ENVIRONMENTS = frozenset(
    {
        "LOCAL_TEST",
        "CI",
        "RESEARCH",
        "PREPRODUCTION",
        "STAGING",
        "LIVE_EXTERNAL",
        "PRODUCTION",
    }
)
NONE_AUTHORITY_FIELDS = (
    "financial_authority",
    "payment_authority",
    "accounting_authority",
    "execution_authority",
    "signing_authority",
    "blockchain_submission_authority",
    "production_deployment_authority",
    "merge_authority",
)


class ArtifactEvidenceEnvelopeV1Error(ValueError):
    pass


def canonical_digest(value: Mapping[str, Any]) -> str:
    body = dict(value)
    body.pop("envelope_digest", None)
    encoded = json.dumps(
        body,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ArtifactEvidenceEnvelopeV1Error(f"{name} required")
    if value != value.strip():
        raise ArtifactEvidenceEnvelopeV1Error(f"{name} must be canonical text")
    return value


def _hex(value: Any, name: str, length: int) -> str:
    text = _text(value, name)
    alphabet = HEX40 if length == 40 else HEX64
    if len(text) != length or any(ch not in alphabet for ch in text):
        raise ArtifactEvidenceEnvelopeV1Error(f"{name} must be lowercase hex{length}")
    return text


def _repository(value: Any, name: str) -> str:
    text = _text(value, name)
    if not text.startswith("Shtenco/") or text.count("/") != 1:
        raise ArtifactEvidenceEnvelopeV1Error(f"{name} must be Shtenco/repository")
    return text


def _time(value: Any, name: str) -> str:
    text = _text(value, name)
    if not text.endswith("Z"):
        raise ArtifactEvidenceEnvelopeV1Error(f"{name} must use UTC Z")
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError as exc:
        raise ArtifactEvidenceEnvelopeV1Error(f"{name} invalid timestamp") from exc
    if parsed.isoformat().replace("+00:00", "Z") != text:
        raise ArtifactEvidenceEnvelopeV1Error(f"{name} not canonical UTC")
    return text


def verify_artifact_evidence_envelope_v1(
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(payload, Mapping) or payload.get("schema") != SCHEMA:
        raise ArtifactEvidenceEnvelopeV1Error("unsupported envelope schema")
    if set(payload) != TOP_LEVEL_FIELDS:
        raise ArtifactEvidenceEnvelopeV1Error("envelope top-level fields mismatch")

    item = dict(payload)
    supplied_digest = _hex(item.get("envelope_digest"), "envelope_digest", 64)
    if canonical_digest(item) != supplied_digest:
        raise ArtifactEvidenceEnvelopeV1Error("envelope digest mismatch")

    _text(item.get("envelope_id"), "envelope_id")
    _text(item.get("artifact_type"), "artifact_type")
    _text(item.get("artifact_schema"), "artifact_schema")
    _hex(item.get("artifact_digest"), "artifact_digest", 64)
    _repository(item.get("source_repository"), "source_repository")
    _hex(item.get("source_commit"), "source_commit", 40)
    _repository(item.get("producer_repository"), "producer_repository")

    if item.get("authority_domain") not in AUTHORITY_DOMAINS:
        raise ArtifactEvidenceEnvelopeV1Error("authority_domain unsupported")
    if item.get("authority_scope") != AUTHORITY_SCOPE:
        raise ArtifactEvidenceEnvelopeV1Error("authority_scope escalation")
    if item.get("environment") not in ENVIRONMENTS:
        raise ArtifactEvidenceEnvelopeV1Error("environment unsupported")
    if item.get("evidence_status") != EVIDENCE_STATUS:
        raise ArtifactEvidenceEnvelopeV1Error("envelope cannot self-promote evidence status")
    _text(item.get("source_status_text"), "source_status_text")

    source_verifier_digest = item.get("source_verifier_digest")
    if source_verifier_digest is not None:
        _hex(source_verifier_digest, "source_verifier_digest", 64)

    _time(item.get("observed_at"), "observed_at")

    parent_digests = item.get("parent_digests")
    if not isinstance(parent_digests, list):
        raise ArtifactEvidenceEnvelopeV1Error("parent_digests must be list")
    normalized_parents = [
        _hex(value, f"parent_digests[{index}]", 64)
        for index, value in enumerate(parent_digests)
    ]
    if normalized_parents != sorted(set(normalized_parents)):
        raise ArtifactEvidenceEnvelopeV1Error(
            "parent_digests must be sorted and unique"
        )

    metadata = item.get("metadata")
    if not isinstance(metadata, Mapping) or set(metadata) != METADATA_FIELDS:
        raise ArtifactEvidenceEnvelopeV1Error("metadata fields mismatch")
    _text(metadata.get("artifact_path"), "metadata.artifact_path")
    _text(metadata.get("content_media_type"), "metadata.content_media_type")
    _text(metadata.get("human_label"), "metadata.human_label")

    for field in NONE_AUTHORITY_FIELDS:
        if item.get(field) != "NONE":
            raise ArtifactEvidenceEnvelopeV1Error(f"{field} escalation")

    return item


verify_envelope = verify_artifact_evidence_envelope_v1
