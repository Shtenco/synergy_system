from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "repository_engineering_baseline_v1",
    ROOT / "src" / "synergy_system" / "repository_engineering_baseline_v1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

POLICY_PATH = ROOT / "config" / "repository_engineering_baseline_policy_v1.json"


def policy():
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def assessment(status: str = "NOT_ASSESSED"):
    p = policy()
    index = MOD.policy_index(p)
    repositories = []
    for name in sorted(index):
        profile, required_controls = index[name]
        controls = []
        for control_name in sorted(required_controls):
            if status == "NOT_ASSESSED":
                evidence_digest = None
                evidence_source = None
            else:
                evidence_digest = MOD.canonical_digest(
                    {"repository": name, "control": control_name, "status": status},
                    "unused",
                )
                evidence_source = f"evidence://{name}/{control_name}"
            controls.append(
                {
                    "control": control_name,
                    "status": status,
                    "evidence_digest": evidence_digest,
                    "evidence_source": evidence_source,
                }
            )
        repositories.append({"repository": name, "profile": profile, "controls": controls})
    value = {
        "schema": MOD.ASSESSMENT_SCHEMA,
        "assessment_id": "STRUCTURAL_TEST_ONLY_NOT_COMPLIANCE_EVIDENCE",
        "policy_digest": MOD.EXPECTED_POLICY_DIGEST,
        "federation_digest": MOD.EXPECTED_FEDERATION_DIGEST,
        "generated_at": "2026-09-04T17:30:00Z",
        "repositories": repositories,
        "overall_status": MOD.derive_overall_status(repositories),
        "portfolio_compliance_claim": False,
        "promotion_authority": "NONE",
    }
    value["assessment_digest"] = MOD.canonical_digest(value, "assessment_digest")
    return value


def rehash(value):
    value["assessment_digest"] = MOD.canonical_digest(value, "assessment_digest")
    return value


def test_policy_is_pinned_and_covers_all_42_exactly_once():
    verified = MOD.verify_policy(policy())
    index = MOD.policy_index(verified)
    assert verified["repository_count"] == 42
    assert set(index) == MOD.EXPECTED_REPOSITORIES
    assert len(index) == 42
    assert verified["auto_merge"] is False
    assert verified["merge_policy"] == "HUMAN_MAINTAINER_ONLY"
    assert all(value == "NONE" for value in verified["global_authorities"].values())


def test_fresh_rehash_cannot_weaken_pinned_policy():
    value = policy()
    value["auto_merge"] = True
    value["digest"] = MOD.canonical_digest(value, "digest")
    with pytest.raises(MOD.RepositoryEngineeringBaselineV1Error, match="policy digest mismatch"):
        MOD.verify_policy(value)


def test_all_unknown_evidence_is_incomplete_not_compliant():
    value = assessment()
    verified = MOD.verify_assessment(value, policy())
    assert verified["overall_status"] == "INCOMPLETE_NOT_ASSESSED"
    assert verified["portfolio_compliance_claim"] is False
    assert verified["promotion_authority"] == "NONE"


def test_all_pass_is_only_pending_independent_review_not_self_compliance():
    value = assessment("EVIDENCED_PASS")
    verified = MOD.verify_assessment(value, policy())
    assert verified["overall_status"] == "EVIDENCE_COMPLETE_PENDING_INDEPENDENT_REVIEW"
    assert verified["portfolio_compliance_claim"] is False


def test_one_evidenced_failure_dominates_overall_status():
    value = assessment("EVIDENCED_PASS")
    value["repositories"][0]["controls"][0]["status"] = "EVIDENCED_FAIL"
    value["repositories"][0]["controls"][0]["evidence_digest"] = "f" * 64
    value["repositories"][0]["controls"][0]["evidence_source"] = "evidence://failure"
    value["overall_status"] = MOD.derive_overall_status(value["repositories"])
    rehash(value)
    verified = MOD.verify_assessment(value, policy())
    assert verified["overall_status"] == "EVIDENCED_FAILURE_PRESENT"


def test_fake_pass_without_evidence_fails_closed():
    value = assessment()
    control = value["repositories"][0]["controls"][0]
    control["status"] = "EVIDENCED_PASS"
    value["overall_status"] = MOD.derive_overall_status(value["repositories"])
    rehash(value)
    with pytest.raises(MOD.RepositoryEngineeringBaselineV1Error, match="control evidence_digest"):
        MOD.verify_assessment(value, policy())


def test_not_assessed_cannot_smuggle_evidence():
    value = assessment()
    control = value["repositories"][0]["controls"][0]
    control["evidence_digest"] = "a" * 64
    control["evidence_source"] = "evidence://smuggled"
    rehash(value)
    with pytest.raises(MOD.RepositoryEngineeringBaselineV1Error, match="NOT_ASSESSED cannot carry evidence"):
        MOD.verify_assessment(value, policy())


def test_missing_repository_and_wrong_profile_fail():
    value = assessment()
    value["repositories"].pop()
    rehash(value)
    with pytest.raises(MOD.RepositoryEngineeringBaselineV1Error, match="repository coverage mismatch"):
        MOD.verify_assessment(value, policy())

    value = assessment()
    value["repositories"][0]["profile"] = "RUNTIME_PRODUCT" if value["repositories"][0]["profile"] != "RUNTIME_PRODUCT" else "RESEARCH"
    rehash(value)
    with pytest.raises(MOD.RepositoryEngineeringBaselineV1Error, match="profile mismatch"):
        MOD.verify_assessment(value, policy())


def test_control_coverage_is_exact_for_profile():
    value = assessment()
    value["repositories"][0]["controls"].pop()
    rehash(value)
    with pytest.raises(MOD.RepositoryEngineeringBaselineV1Error, match="control coverage mismatch"):
        MOD.verify_assessment(value, policy())


def test_hidden_field_self_certification_fails_even_after_fresh_rehash():
    value = assessment()
    value["live_compliant"] = True
    rehash(value)
    with pytest.raises(MOD.RepositoryEngineeringBaselineV1Error, match="top-level fields mismatch"):
        MOD.verify_assessment(value, policy())


def test_portfolio_compliance_and_promotion_authority_cannot_self_escalate():
    value = assessment("EVIDENCED_PASS")
    value["portfolio_compliance_claim"] = True
    rehash(value)
    with pytest.raises(MOD.RepositoryEngineeringBaselineV1Error, match="cannot self-certify"):
        MOD.verify_assessment(value, policy())

    value = assessment()
    value["promotion_authority"] = "AI"
    rehash(value)
    with pytest.raises(MOD.RepositoryEngineeringBaselineV1Error, match="promotion authority escalation"):
        MOD.verify_assessment(value, policy())


def test_assessment_digest_tamper_fails():
    value = assessment()
    value["assessment_id"] = "tampered"
    with pytest.raises(MOD.RepositoryEngineeringBaselineV1Error, match="assessment digest mismatch"):
        MOD.verify_assessment(value, policy())
