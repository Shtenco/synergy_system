import json
from pathlib import Path

import pytest

from synergy_system.governance_lint_v3 import (
    GovernanceLintError,
    assert_patch_allowed,
    lint_patch,
    validate_authority_policy,
    validate_schema_registry,
)

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((ROOT / "config" / name).read_text(encoding="utf-8"))


def repos():
    return set(load("expected_repositories_v1.json")["repositories"])


def test_registry_and_policy_validate_against_frozen_federation():
    validate_schema_registry(load("cross_repo_schema_registry_v1.json"), repos())
    validate_authority_policy(load("authority_lint_policy_v1.json"), repos())


def test_synergynet_cannot_claim_accounting_authority_in_source_patch():
    findings = lint_patch(
        repository="Shtenco/synergynet",
        path="src/synergynet/evil.py",
        patch='+accounting_authority = "CANONICAL"\n',
        policy=load("authority_lint_policy_v1.json"),
        expected_repositories=repos(),
    )
    assert len(findings) == 1
    assert findings[0].field == "accounting_authority"


def test_science_agent_cannot_claim_scientific_truth_authority():
    with pytest.raises(GovernanceLintError, match="scientific_truth_authority"):
        assert_patch_allowed(
            repository="Shtenco/nexus_science_agent",
            path="config/policy.json",
            patch='+  "scientific_truth_authority": "TRUTH"\n',
            policy=load("authority_lint_policy_v1.json"),
            expected_repositories=repos(),
        )


def test_none_authority_is_allowed_everywhere_and_docs_are_not_scanned():
    assert lint_patch(
        repository="Shtenco/agi_nexus", path="src/agi_nexus/model.py",
        patch='+execution_authority: str = "NONE"\n', policy=load("authority_lint_policy_v1.json"),
        expected_repositories=repos(),
    ) == ()
    assert lint_patch(
        repository="Shtenco/synergynet", path="docs/example.md",
        patch='+accounting_authority = "TREASURY"\n', policy=load("authority_lint_policy_v1.json"),
        expected_repositories=repos(),
    ) == ()


def test_declared_owner_is_not_blocked_by_ownership_linter():
    assert lint_patch(
        repository="Shtenco/synergy_financial_os", path="src/domain.py",
        patch='+accounting_authority = "CANONICAL_FINANCIAL_OS"\n',
        policy=load("authority_lint_policy_v1.json"), expected_repositories=repos(),
    ) == ()


def test_unknown_schema_producer_is_rejected():
    registry = load("cross_repo_schema_registry_v1.json")
    registry["contracts"][0]["producer"] = "Shtenco/not-a-repo"
    with pytest.raises(GovernanceLintError, match="unknown schema producer"):
        validate_schema_registry(registry, repos())


def test_duplicate_schema_generation_is_rejected():
    registry = load("cross_repo_schema_registry_v1.json")
    registry["contracts"].append(dict(registry["contracts"][0]))
    with pytest.raises(GovernanceLintError, match="unique versioned"):
        validate_schema_registry(registry, repos())
