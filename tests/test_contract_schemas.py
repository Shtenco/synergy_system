import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
SCHEMAS=ROOT/"contracts"/"schemas"

def test_all_json_schemas_are_valid_draft_2020_12():
    files=sorted(SCHEMAS.glob("*.schema.json"))
    assert len(files) >= 17
    for path in files:
        schema=json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
