from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

POLICY_SCHEMA = "synergy.repository-engineering-baseline-policy/v1"
ASSESSMENT_SCHEMA = "synergy.repository-engineering-baseline-assessment/v1"
EXPECTED_POLICY_DIGEST = "8ba39de2763c72eb99e7586c34bbbeac6caac9cf5904639373d6eca5a0d883ec"
EXPECTED_FEDERATION_DIGEST = "7de7c2dda23db2581294176bb262ae4aa8cbdc4ba97cdd4326278e88a9713a05"
ARTIFACT_ENVELOPE_SCHEMA = "synergy.artifact-evidence-envelope/v1"
PROFILE_NAMES = frozenset(
    {"RUNTIME_PRODUCT", "ENGINEERING_TOOLING", "RESEARCH", "PRESENTATION", "LEGACY_PLACEHOLDER"}
)
EVIDENCE_STATUSES = frozenset({"EVIDENCED_PASS", "EVIDENCED_FAIL", "NOT_ASSESSED"})
AUTHORITY_FIELDS = (
    "financial_authority",
    "payment_authority",
    "accounting_authority",
    "execution_authority",
    "signing_authority",
    "blockchain_submission_authority",
    "production_deployment_authority",
    "merge_execution_authority",
    "ai_authority",
)
ASSESSMENT_TOP_LEVEL_FIELDS = frozenset(
    {
        "schema",
        "assessment_id",
        "policy_digest",
        "federation_digest",
        "generated_at",
        "repositories",
        "overall_status",
        "portfolio_compliance_claim",
        "promotion_authority",
        "assessment_digest",
    }
)
REPOSITORY_ASSESSMENT_FIELDS = frozenset({"repository", "profile", "controls"})
CONTROL_FIELDS = frozenset({"control", "status", "evidence_digest", "evidence_source"})

EXPECTED_REPOSITORIES = frozenset(
    {
        "Shtenco/3D_bars_market_structure",
        "Shtenco/agi_autopilot",
        "Shtenco/agi_nexus",
        "Shtenco/agi_olga",
        "Shtenco/ai_coder",
        "Shtenco/ai_compress",
        "Shtenco/ai_financial_system",
        "Shtenco/ai_language",
        "Shtenco/ai_trade_terminal",
        "Shtenco/algotrading_graph_system",
        "Shtenco/binary_quantum_theory",
        "Shtenco/blochain_budget",
        "Shtenco/cashero",
        "Shtenco/cold_nuclear",
        "Shtenco/computer_vision_trading_metatrader_5",
        "Shtenco/cross_forex_arbitrage_trading_metatrader_5",
        "Shtenco/global_liquidity_dataminer",
        "Shtenco/midas_ai",
        "Shtenco/midas_ai_trading_system",
        "Shtenco/midas_lite",
        "Shtenco/multi_threaded_trading_robot_with_machine_learning_python",
        "Shtenco/nexus_science_agent",
        "Shtenco/qr_compress",
        "Shtenco/quantum-trading_metatrader5",
        "Shtenco/shtenco.github.io",
        "Shtenco/shtencoauantai.github.io",
        "Shtenco/sinergy-super-app",
        "Shtenco/sinergy_app",
        "Shtenco/swap_arbitrage_metatrader_5",
        "Shtenco/synergy_ai_blockchain",
        "Shtenco/synergy_app",
        "Shtenco/synergy_eurasian",
        "Shtenco/synergy_financial_os",
        "Shtenco/synergy_matrix_sota",
        "Shtenco/synergy_meta_os",
        "Shtenco/synergy_pay_system",
        "Shtenco/synergy_system",
        "Shtenco/synergychain",
        "Shtenco/synergychain.github.io",
        "Shtenco/synergynet",
        "Shtenco/turbo_linux",
        "Shtenco/usds",
    }
)


class RepositoryEngineeringBaselineV1Error(ValueError):
    pass


def canonical_digest(value: Mapping[str, Any], digest_field: str) -> str:
    body = dict(value)
    body.pop(digest_field, None)
    encoded = json.dumps(
        body,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise RepositoryEngineeringBaselineV1Error(f"{name} must be canonical non-empty text")
    return value


def _hex64(value: Any, name: str) -> str:
    text = _text(value, name)
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise RepositoryEngineeringBaselineV1Error(f"{name} must be lowercase sha256")
    return text


def _time(value: Any, name: str) -> str:
    text = _text(value, name)
    if not text.endswith("Z"):
        raise RepositoryEngineeringBaselineV1Error(f"{name} must be canonical UTC Z")
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError as exc:
        raise RepositoryEngineeringBaselineV1Error(f"{name} invalid timestamp") from exc
    if parsed.isoformat().replace("+00:00", "Z") != text:
        raise RepositoryEngineeringBaselineV1Error(f"{name} not canonical UTC")
    return text


def verify_policy(policy: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(policy, Mapping) or policy.get("schema") != POLICY_SCHEMA:
        raise RepositoryEngineeringBaselineV1Error("unsupported policy schema")
    supplied = _hex64(policy.get("digest"), "policy digest")
    computed = canonical_digest(policy, "digest")
    if supplied != EXPECTED_POLICY_DIGEST or computed != EXPECTED_POLICY_DIGEST:
        raise RepositoryEngineeringBaselineV1Error("policy digest mismatch")
    if policy.get("federation_digest") != EXPECTED_FEDERATION_DIGEST:
        raise RepositoryEngineeringBaselineV1Error("federation root mismatch")
    if policy.get("artifact_evidence_envelope_schema") != ARTIFACT_ENVELOPE_SCHEMA:
        raise RepositoryEngineeringBaselineV1Error("artifact envelope schema mismatch")
    if policy.get("repository_count") != 42:
        raise RepositoryEngineeringBaselineV1Error("repository count mismatch")
    if policy.get("merge_policy") != "HUMAN_MAINTAINER_ONLY" or policy.get("auto_merge") is not False:
        raise RepositoryEngineeringBaselineV1Error("merge policy escalation")
    if policy.get("unknown_or_missing_evidence_status") != "NOT_ASSESSED":
        raise RepositoryEngineeringBaselineV1Error("unknown evidence must fail closed")
    if policy.get("policy_status") != "BASELINE_POLICY_DEFINED_NO_REPOSITORY_COMPLIANCE_CLAIM":
        raise RepositoryEngineeringBaselineV1Error("policy status escalation")

    authorities = policy.get("global_authorities")
    if not isinstance(authorities, Mapping) or set(authorities) != set(AUTHORITY_FIELDS):
        raise RepositoryEngineeringBaselineV1Error("global authority fields mismatch")
    if any(authorities[field] != "NONE" for field in AUTHORITY_FIELDS):
        raise RepositoryEngineeringBaselineV1Error("global authority escalation")

    profiles = policy.get("profiles")
    if not isinstance(profiles, Mapping) or set(profiles) != PROFILE_NAMES:
        raise RepositoryEngineeringBaselineV1Error("profile set mismatch")

    seen: list[str] = []
    for profile_name in sorted(PROFILE_NAMES):
        profile = profiles[profile_name]
        if not isinstance(profile, Mapping):
            raise RepositoryEngineeringBaselineV1Error("profile must be object")
        repositories = profile.get("repositories")
        controls = profile.get("required_controls")
        if not isinstance(repositories, list) or repositories != sorted(set(repositories)):
            raise RepositoryEngineeringBaselineV1Error(f"{profile_name} repositories must be sorted unique")
        if not isinstance(controls, list) or not controls or len(controls) != len(set(controls)):
            raise RepositoryEngineeringBaselineV1Error(f"{profile_name} controls invalid")
        if not isinstance(profile.get("production_claim_requires_all_controls_evidenced"), bool):
            raise RepositoryEngineeringBaselineV1Error(f"{profile_name} promotion rule invalid")
        seen.extend(repositories)

    if len(seen) != 42 or set(seen) != EXPECTED_REPOSITORIES or len(seen) != len(set(seen)):
        raise RepositoryEngineeringBaselineV1Error("policy must cover each federation repository exactly once")
    return dict(policy)


def policy_index(policy: Mapping[str, Any]) -> dict[str, tuple[str, tuple[str, ...]]]:
    verified = verify_policy(policy)
    result: dict[str, tuple[str, tuple[str, ...]]] = {}
    for profile_name, profile in verified["profiles"].items():
        controls = tuple(profile["required_controls"])
        for repository in profile["repositories"]:
            result[repository] = (profile_name, controls)
    return result


def derive_overall_status(repositories: list[Mapping[str, Any]]) -> str:
    statuses = [control["status"] for repo in repositories for control in repo["controls"]]
    if any(status == "EVIDENCED_FAIL" for status in statuses):
        return "EVIDENCED_FAILURE_PRESENT"
    if statuses and all(status == "EVIDENCED_PASS" for status in statuses):
        return "EVIDENCE_COMPLETE_PENDING_INDEPENDENT_REVIEW"
    return "INCOMPLETE_NOT_ASSESSED"


def verify_assessment(assessment: Mapping[str, Any], policy: Mapping[str, Any]) -> dict[str, Any]:
    index = policy_index(policy)
    if not isinstance(assessment, Mapping) or assessment.get("schema") != ASSESSMENT_SCHEMA:
        raise RepositoryEngineeringBaselineV1Error("unsupported assessment schema")
    if set(assessment) != ASSESSMENT_TOP_LEVEL_FIELDS:
        raise RepositoryEngineeringBaselineV1Error("assessment top-level fields mismatch")
    if assessment.get("policy_digest") != EXPECTED_POLICY_DIGEST:
        raise RepositoryEngineeringBaselineV1Error("assessment policy root mismatch")
    if assessment.get("federation_digest") != EXPECTED_FEDERATION_DIGEST:
        raise RepositoryEngineeringBaselineV1Error("assessment federation root mismatch")
    _text(assessment.get("assessment_id"), "assessment_id")
    _time(assessment.get("generated_at"), "generated_at")
    if assessment.get("portfolio_compliance_claim") is not False:
        raise RepositoryEngineeringBaselineV1Error("assessment cannot self-certify portfolio compliance")
    if assessment.get("promotion_authority") != "NONE":
        raise RepositoryEngineeringBaselineV1Error("assessment promotion authority escalation")

    supplied_digest = _hex64(assessment.get("assessment_digest"), "assessment_digest")
    if canonical_digest(assessment, "assessment_digest") != supplied_digest:
        raise RepositoryEngineeringBaselineV1Error("assessment digest mismatch")

    repositories = assessment.get("repositories")
    if not isinstance(repositories, list):
        raise RepositoryEngineeringBaselineV1Error("repositories assessment must be list")
    names = [repo.get("repository") for repo in repositories if isinstance(repo, Mapping)]
    if names != sorted(EXPECTED_REPOSITORIES) or len(names) != 42:
        raise RepositoryEngineeringBaselineV1Error("assessment repository coverage mismatch")

    for repo in repositories:
        if not isinstance(repo, Mapping) or set(repo) != REPOSITORY_ASSESSMENT_FIELDS:
            raise RepositoryEngineeringBaselineV1Error("repository assessment fields mismatch")
        name = repo["repository"]
        expected_profile, expected_controls = index[name]
        if repo.get("profile") != expected_profile:
            raise RepositoryEngineeringBaselineV1Error(f"{name} profile mismatch")
        controls = repo.get("controls")
        if not isinstance(controls, list):
            raise RepositoryEngineeringBaselineV1Error(f"{name} controls must be list")
        control_names = [x.get("control") for x in controls if isinstance(x, Mapping)]
        if control_names != sorted(expected_controls):
            raise RepositoryEngineeringBaselineV1Error(f"{name} control coverage mismatch")
        for control in controls:
            if not isinstance(control, Mapping) or set(control) != CONTROL_FIELDS:
                raise RepositoryEngineeringBaselineV1Error("control fields mismatch")
            status = control.get("status")
            if status not in EVIDENCE_STATUSES:
                raise RepositoryEngineeringBaselineV1Error("control evidence status unsupported")
            evidence_digest = control.get("evidence_digest")
            evidence_source = control.get("evidence_source")
            if status == "NOT_ASSESSED":
                if evidence_digest is not None or evidence_source is not None:
                    raise RepositoryEngineeringBaselineV1Error("NOT_ASSESSED cannot carry evidence")
            else:
                _hex64(evidence_digest, "control evidence_digest")
                _text(evidence_source, "control evidence_source")

    expected_overall = derive_overall_status(repositories)
    if assessment.get("overall_status") != expected_overall:
        raise RepositoryEngineeringBaselineV1Error("overall assessment status mismatch")
    return dict(assessment)


def load_policy(root: Path) -> dict[str, Any]:
    path = root / "config" / "repository_engineering_baseline_policy_v1.json"
    return json.loads(path.read_text(encoding="utf-8"))
