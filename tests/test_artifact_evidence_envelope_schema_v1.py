from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "artifact_evidence_envelope_v1_schema_parity",
    ROOT / "src" / "synergy_system" / "artifact_evidence_envelope_v1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

SCHEMA_PATH = ROOT / "schemas" / "artifact_evidence_envelope_v1.schema.json"


def schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_schema_exact_top_level_matches_runtime_contract():
    value = schema()
    assert value["additionalProperties"] is False
    assert set(value["properties"]) == MOD.TOP_LEVEL_FIELDS
    assert set(value["required"]) == MOD.TOP_LEVEL_FIELDS


def test_schema_metadata_exact_fields_match_runtime_contract():
    metadata = schema()["properties"]["metadata"]
    assert metadata["additionalProperties"] is False
    assert set(metadata["properties"]) == MOD.METADATA_FIELDS
    assert set(metadata["required"]) == MOD.METADATA_FIELDS


def test_schema_constants_match_runtime_non_authority_contract():
    props = schema()["properties"]
    assert props["schema"]["const"] == MOD.SCHEMA
    assert props["authority_scope"]["const"] == MOD.AUTHORITY_SCOPE
    assert props["evidence_status"]["const"] == MOD.EVIDENCE_STATUS
    for field in MOD.NONE_AUTHORITY_FIELDS:
        assert props[field]["const"] == "NONE"


def test_schema_vocabularies_match_runtime_vocabularies():
    props = schema()["properties"]
    assert set(props["authority_domain"]["enum"]) == MOD.AUTHORITY_DOMAINS
    assert set(props["environment"]["enum"]) == MOD.ENVIRONMENTS
