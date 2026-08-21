from copy import deepcopy
from pathlib import Path

import pytest

from synergy_system import FederationError, load_expected_repositories, load_federation, validate_federation

ROOT = Path(__file__).resolve().parents[1]


def _load():
    payload = load_federation(ROOT / "config/repository_federation_v1.yaml")
    expected = load_expected_repositories(ROOT / "config/expected_repositories_v1.json")
    return payload, expected


def test_current_federation_is_complete_and_valid():
    payload, expected = _load()
    validate_federation(payload, expected)
    assert len(payload["repositories"]) == 37
    assert len(payload["exclusive_authorities"]) == 15


def test_missing_repository_is_rejected():
    payload, expected = _load()
    broken = deepcopy(payload)
    broken["repositories"] = broken["repositories"][:-1]
    with pytest.raises(FederationError):
        validate_federation(broken, expected)


def test_presentation_repo_cannot_gain_authority():
    payload, expected = _load()
    broken = deepcopy(payload)
    entry = next(item for item in broken["repositories"] if item["repo"] == "Shtenco/synergychain.github.io")
    entry["authority"] = "TREASURY"
    with pytest.raises(FederationError):
        validate_federation(broken, expected)


def test_ai_cannot_gain_direct_payment_fact_edge():
    payload, expected = _load()
    broken = deepcopy(payload)
    broken["canonical_dependency_direction"].append({
        "from": "Shtenco/agi_nexus",
        "to": "Shtenco/synergy_pay_system",
        "contract": "direct_payment_execution",
    })
    with pytest.raises(FederationError):
        validate_federation(broken, expected)


def test_unexpected_bidirectional_cycle_is_rejected():
    payload, expected = _load()
    broken = deepcopy(payload)
    broken["canonical_dependency_direction"].append({
        "from": "Shtenco/ai_coder",
        "to": "Shtenco/ai_language",
        "contract": "reverse_requirement_authority",
    })
    with pytest.raises(FederationError):
        validate_federation(broken, expected)


def test_duplicate_yaml_key_is_rejected_before_semantic_validation(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("schema: one\nschema: two\n", encoding="utf-8")
    with pytest.raises(FederationError):
        load_federation(path)
