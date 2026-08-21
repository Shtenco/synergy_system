from pathlib import Path

import pytest

from synergy_system.graph import build_architecture_graph, to_dot
from synergy_system.live_audit import LiveAuditAuthRequired, GitHubRestProvider, audit_repositories, verify_live_audit
from synergy_system.validator import load_expected_repositories, load_federation

ROOT = Path(__file__).resolve().parents[1]


class FakeProvider:
    def __init__(self, missing=()):
        self.missing = set(missing)

    def repository(self, full_name):
        if full_name in self.missing:
            raise FileNotFoundError(full_name)
        return {
            "full_name": full_name,
            "default_branch": "main",
            "private": full_name in {"Shtenco/synergy_system", "Shtenco/midas_ai"},
            "archived": False,
            "disabled": False,
        }


def expected():
    return load_expected_repositories(ROOT / "config/expected_repositories_v1.json")


def test_architecture_graph_is_deterministic_and_exposes_only_intentional_cycle():
    federation = load_federation(ROOT / "config/repository_federation_v1.yaml")
    first = build_architecture_graph(federation)
    second = build_architecture_graph(federation)
    assert first.digest == second.digest
    assert first.artifact["cyclic_components"] == [["Shtenco/synergy_financial_os", "Shtenco/synergy_pay_system"]]
    dot = to_dot(first)
    assert '"Shtenco/agi_nexus" -> "Shtenco/nexus_science_agent"' in dot
    assert first.artifact["execution_authority"] == "NONE"


def test_live_audit_complete_snapshot_round_trip():
    repos = expected()
    artifact = audit_repositories(repos, FakeProvider(), observed_at="2026-08-21T07:00:00Z")
    verify_live_audit(artifact, repos)
    assert artifact["audit_status"] == "COMPLETE"
    assert artifact["observed_repository_count"] == 37
    assert artifact["missing_repositories"] == []


def test_missing_repo_is_explicit_not_silently_ignored():
    repos = expected()
    missing = "Shtenco/agi_nexus"
    artifact = audit_repositories(repos, FakeProvider([missing]), observed_at="2026-08-21T07:00:00Z")
    verify_live_audit(artifact, repos)
    assert artifact["audit_status"] == "INCOMPLETE"
    assert artifact["missing_repositories"] == [missing]


def test_fresh_hash_cannot_grant_audit_authority():
    repos = expected()
    artifact = audit_repositories(repos, FakeProvider(), observed_at="2026-08-21T07:00:00Z")
    artifact["execution_authority"] = "DEPLOY"
    import hashlib, json
    body = dict(artifact)
    body.pop("digest")
    artifact["digest"] = hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    with pytest.raises(Exception):
        verify_live_audit(artifact, repos)


def test_private_live_audit_requires_explicit_read_only_credential():
    with pytest.raises(LiveAuditAuthRequired):
        GitHubRestProvider(token="")
