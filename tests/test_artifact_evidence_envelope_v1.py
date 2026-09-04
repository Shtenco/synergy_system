from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "artifact_evidence_envelope_v1",
    ROOT / "src" / "synergy_system" / "artifact_evidence_envelope_v1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

FIXTURES = ROOT / "fixtures" / "artifact_evidence_envelope_v1_examples.json"
EXPECTED_REPOSITORIES = {
    "Shtenco/synergy_financial_os",
    "Shtenco/synergy_pay_system",
    "Shtenco/synergy_ai_blockchain",
    "Shtenco/agi_nexus",
    "Shtenco/midas_ai",
    "Shtenco/synergy_app",
}
EXPECTED_DOMAINS = {
    "FINANCIAL_ACCOUNTING",
    "SETTLEMENT",
    "TRUST_COMMITMENT",
    "AI_INFERENCE",
    "TRADING_PROPOSAL",
    "CLIENT_PRESENTATION",
}


def examples():
    return json.loads(FIXTURES.read_text(encoding="utf-8"))


def rehash(value):
    value["envelope_digest"] = MOD.canonical_digest(value)
    return value


def one():
    return copy.deepcopy(examples()[0])


def test_all_six_conformance_examples_validate_and_cover_six_domains():
    values = examples()
    assert len(values) == 6
    assert {x["source_repository"] for x in values} == EXPECTED_REPOSITORIES
    assert {x["authority_domain"] for x in values} == EXPECTED_DOMAINS
    for value in values:
        verified = MOD.verify_envelope(value)
        assert verified["envelope_digest"] == value["envelope_digest"]
        assert verified["evidence_status"] == "PROVENANCE_ENVELOPE_ONLY"
        assert verified["authority_scope"] == "IDENTITY_AND_PROVENANCE_ONLY"
        for field in MOD.NONE_AUTHORITY_FIELDS:
            assert verified[field] == "NONE"


def test_digest_tamper_without_rehash_fails():
    value = one()
    value["artifact_digest"] = "f" * 64
    with pytest.raises(MOD.ArtifactEvidenceEnvelopeV1Error, match="envelope digest mismatch"):
        MOD.verify_envelope(value)


def test_hidden_top_level_live_claim_fails_even_after_fresh_rehash():
    value = one()
    value["live_execution_claim"] = True
    rehash(value)
    with pytest.raises(MOD.ArtifactEvidenceEnvelopeV1Error, match="top-level fields mismatch"):
        MOD.verify_envelope(value)


def test_hidden_metadata_authority_fails_even_after_fresh_rehash():
    value = one()
    value["metadata"]["execution_authority"] = "AI"
    rehash(value)
    with pytest.raises(MOD.ArtifactEvidenceEnvelopeV1Error, match="metadata fields mismatch"):
        MOD.verify_envelope(value)


def test_evidence_status_cannot_self_promote_after_fresh_rehash():
    value = one()
    value["evidence_status"] = "LIVE_VERIFIED"
    rehash(value)
    with pytest.raises(MOD.ArtifactEvidenceEnvelopeV1Error, match="cannot self-promote"):
        MOD.verify_envelope(value)


def test_authority_scope_cannot_escalate_after_fresh_rehash():
    value = one()
    value["authority_scope"] = "EXECUTION_AUTHORITY"
    rehash(value)
    with pytest.raises(MOD.ArtifactEvidenceEnvelopeV1Error, match="authority_scope escalation"):
        MOD.verify_envelope(value)


@pytest.mark.parametrize("field", MOD.NONE_AUTHORITY_FIELDS)
def test_each_operational_authority_is_permanently_none(field):
    value = one()
    value[field] = "AI"
    rehash(value)
    with pytest.raises(MOD.ArtifactEvidenceEnvelopeV1Error, match=f"{field} escalation"):
        MOD.verify_envelope(value)


def test_parent_digests_must_be_sorted_and_unique():
    value = one()
    value["parent_digests"] = ["b" * 64, "a" * 64]
    rehash(value)
    with pytest.raises(MOD.ArtifactEvidenceEnvelopeV1Error, match="sorted and unique"):
        MOD.verify_envelope(value)

    value = one()
    value["parent_digests"] = ["a" * 64, "a" * 64]
    rehash(value)
    with pytest.raises(MOD.ArtifactEvidenceEnvelopeV1Error, match="sorted and unique"):
        MOD.verify_envelope(value)


def test_timestamp_must_be_canonical_utc_z():
    value = one()
    value["observed_at"] = "2026-08-29T19:21:00.000Z"
    rehash(value)
    with pytest.raises(MOD.ArtifactEvidenceEnvelopeV1Error, match="not canonical UTC"):
        MOD.verify_envelope(value)


def test_source_repository_must_be_shtenco_repository():
    value = one()
    value["source_repository"] = "attacker/repo"
    rehash(value)
    with pytest.raises(MOD.ArtifactEvidenceEnvelopeV1Error, match="must be Shtenco/repository"):
        MOD.verify_envelope(value)


def test_source_commit_and_artifact_digest_must_be_lowercase_exact_hex():
    value = one()
    value["source_commit"] = "A" * 40
    rehash(value)
    with pytest.raises(MOD.ArtifactEvidenceEnvelopeV1Error, match="source_commit must be lowercase hex40"):
        MOD.verify_envelope(value)

    value = one()
    value["artifact_digest"] = "A" * 64
    rehash(value)
    with pytest.raises(MOD.ArtifactEvidenceEnvelopeV1Error, match="artifact_digest must be lowercase hex64"):
        MOD.verify_envelope(value)


def test_source_verifier_digest_when_present_must_be_sha256():
    value = one()
    value["source_verifier_digest"] = "not-a-digest"
    rehash(value)
    with pytest.raises(MOD.ArtifactEvidenceEnvelopeV1Error, match="source_verifier_digest must be lowercase hex64"):
        MOD.verify_envelope(value)


def test_unknown_environment_and_domain_fail_closed_after_rehash():
    value = one()
    value["environment"] = "MAGIC_PRODUCTION"
    rehash(value)
    with pytest.raises(MOD.ArtifactEvidenceEnvelopeV1Error, match="environment unsupported"):
        MOD.verify_envelope(value)

    value = one()
    value["authority_domain"] = "SUPERUSER"
    rehash(value)
    with pytest.raises(MOD.ArtifactEvidenceEnvelopeV1Error, match="authority_domain unsupported"):
        MOD.verify_envelope(value)


def test_production_or_live_environment_does_not_grant_authority():
    for environment in ("LIVE_EXTERNAL", "PRODUCTION"):
        value = one()
        value["environment"] = environment
        rehash(value)
        verified = MOD.verify_envelope(value)
        assert verified["evidence_status"] == "PROVENANCE_ENVELOPE_ONLY"
        for field in MOD.NONE_AUTHORITY_FIELDS:
            assert verified[field] == "NONE"


def test_source_status_text_is_provenance_text_not_self_certification():
    value = one()
    value["source_status_text"] = "LIVE_VERIFIED_BY_SOURCE_TEXT_ONLY"
    rehash(value)
    verified = MOD.verify_envelope(value)
    assert verified["source_status_text"] == "LIVE_VERIFIED_BY_SOURCE_TEXT_ONLY"
    assert verified["evidence_status"] == "PROVENANCE_ENVELOPE_ONLY"
    assert verified["execution_authority"] == "NONE"
