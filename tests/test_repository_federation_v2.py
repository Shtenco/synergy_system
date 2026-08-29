from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from verify.verify_repository_federation_v2 import (
    FederationError,
    compute_federation_digest,
    verify_federation,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "repository_federation_v2_20260829.json"


@pytest.fixture()
def registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def _rehash(data):
    data["federation_digest"] = compute_federation_digest(data)
    return data


def test_canonical_registry_passes(registry):
    result = verify_federation(registry)
    assert result["status"] == "PASS"
    assert result["repository_count"] == 42
    assert result["covered_steps"] == list(range(1, 21))


def test_duplicate_repository_fails_even_after_fresh_hash(registry):
    bad = copy.deepcopy(registry)
    bad["repositories"][1]["repository"] = bad["repositories"][0]["repository"]
    _rehash(bad)
    with pytest.raises(FederationError, match="duplicate repository"):
        verify_federation(bad)


def test_missing_repo_fails_even_after_fresh_hash(registry):
    bad = copy.deepcopy(registry)
    bad["repositories"].pop()
    bad["repository_count"] = 41
    _rehash(bad)
    with pytest.raises(FederationError, match="repository_count mismatch"):
        verify_federation(bad)


def test_authority_escalation_fails_even_after_fresh_hash(registry):
    bad = copy.deepcopy(registry)
    bad["policy"]["ai_payment_authority"] = "DIRECT"
    _rehash(bad)
    with pytest.raises(FederationError, match="policy mismatch"):
        verify_federation(bad)


def test_auto_merge_enablement_fails_even_after_fresh_hash(registry):
    bad = copy.deepcopy(registry)
    bad["policy"]["auto_merge"] = True
    _rehash(bad)
    with pytest.raises(FederationError, match="policy mismatch"):
        verify_federation(bad)


def test_hidden_repository_field_fails_even_after_fresh_hash(registry):
    bad = copy.deepcopy(registry)
    bad["repositories"][0]["production_verified"] = True
    _rehash(bad)
    with pytest.raises(FederationError, match="repository fields mismatch"):
        verify_federation(bad)


def test_invalid_step_fails_even_after_fresh_hash(registry):
    bad = copy.deepcopy(registry)
    bad["repositories"][0]["top20_steps"].append(21)
    _rehash(bad)
    with pytest.raises(FederationError, match="invalid roadmap step"):
        verify_federation(bad)


def test_digest_tamper_fails(registry):
    bad = copy.deepcopy(registry)
    bad["repositories"][0]["next_milestone"] = "silently changed"
    with pytest.raises(FederationError, match="federation_digest mismatch"):
        verify_federation(bad)
