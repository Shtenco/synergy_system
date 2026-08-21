import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_node_admission_v2_is_meta_os_owned_and_non_executing():
    payload = json.loads((ROOT / "config/cross_repo_schema_overlay_node_admission_v2.json").read_text(encoding="utf-8"))
    assert payload["schema"] == "synergy.cross-repo-schema-overlay/v1"
    assert payload["base_registry"] == "config/cross_repo_schema_registry_v1.json"
    assert payload["additions"] == [{
        "id":"synergy.node-admission-decision/v2",
        "producer":"Shtenco/synergy_meta_os",
        "consumers":["Shtenco/synergy_system"],
        "status":"CURRENT_DRAFT",
        "visibility":"FEDERATION",
        "authority":"NODE_ADMISSION_AUDIT_ONLY",
    }]
    assert payload["execution_authority"] == "NONE"
