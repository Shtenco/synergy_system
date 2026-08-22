import json
from pathlib import Path


def test_source_lock_never_grants_execution_authority() -> None:
    policy = json.loads((Path(__file__).resolve().parents[1] / "config/research_node_build_lock_policy_v1.json").read_text())
    assert policy["source_candidate_execution_authority"] == "NONE"
    assert policy["build_verified_execution_authority"] == "NONE"
    assert policy["allows_source_lock_as_executable_artifact"] is False
    assert policy["requires_new_generation_for_build_verification"] is True
    assert policy["requires_independent_build_evidence"] is True
