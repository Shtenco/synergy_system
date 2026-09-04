import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/research_source_node_build_lock_v1.schema.json"
FIXTURE_PATH = ROOT / "fixtures/node_build_locks/research_compute_node_source_candidate_v1.json"


def test_research_node_build_lock_fixture_matches_canonical_source_lock_schema() -> None:
    schema = json.loads(SCHEMA_PATH.read_text())
    fixture = json.loads(FIXTURE_PATH.read_text())
    jsonschema.validate(fixture, schema)


def test_source_only_v1_cannot_claim_built_artifact_digest() -> None:
    schema = json.loads(SCHEMA_PATH.read_text())
    fixture = json.loads(FIXTURE_PATH.read_text())
    fixture["services"][0]["build_artifact_digest"] = "a" * 64
    fixture["services"][0]["build_status"] = "BUILD_VERIFIED"
    try:
        jsonschema.validate(fixture, schema)
    except jsonschema.ValidationError:
        return
    raise AssertionError("v1 source-only lock unexpectedly accepted built-artifact claim")


def test_legacy_incompatible_schema_is_preserved_but_not_canonical_for_fixture() -> None:
    legacy = json.loads((ROOT / "schemas/synergy_node_build_lock_v1.schema.json").read_text())
    fixture = json.loads(FIXTURE_PATH.read_text())
    try:
        jsonschema.validate(fixture, legacy)
    except jsonschema.ValidationError:
        return
    raise AssertionError("historical incompatible schema unexpectedly matched canonical source-lock fixture")
