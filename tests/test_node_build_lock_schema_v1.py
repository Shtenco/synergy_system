import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]


def test_research_node_build_lock_fixture_matches_schema() -> None:
    schema = json.loads((ROOT / "schemas/synergy_node_build_lock_v1.schema.json").read_text())
    fixture = json.loads((ROOT / "fixtures/node_build_locks/research_compute_node_source_candidate_v1.json").read_text())
    jsonschema.validate(fixture, schema)


def test_build_verified_requires_digest_shape() -> None:
    schema = json.loads((ROOT / "schemas/synergy_node_build_lock_v1.schema.json").read_text())
    fixture = json.loads((ROOT / "fixtures/node_build_locks/research_compute_node_source_candidate_v1.json").read_text())
    fixture["status"] = "BUILD_VERIFIED"
    fixture["build_artifact_digest"] = "not-a-digest"
    try:
        jsonschema.validate(fixture, schema)
    except jsonschema.ValidationError:
        return
    raise AssertionError("invalid build artifact digest unexpectedly passed schema validation")
