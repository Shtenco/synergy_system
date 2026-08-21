from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "config" / "cross_repo_schema_overlay_service_build_recipes_v1.json"


def test_build_recipe_schema_ownership_is_source_local() -> None:
    payload = json.loads(OVERLAY.read_text(encoding="utf-8"))
    entries = {entry["schema_id"]: entry for entry in payload["entries"]}
    assert entries["nexus.service-build-recipe/v1"]["producer"] == "Shtenco/agi_nexus"
    assert entries["nexus-science.service-build-recipe/v1"]["producer"] == "Shtenco/nexus_science_agent"
    assert entries["synergynet.service-build-recipe/v1"]["producer"] == "Shtenco/synergynet"
    assert entries["synergy.service-build-recipe-registry/v1"]["producer"] == "Shtenco/synergy_system"
    assert payload["execution_authority"] == "NONE"


def test_architecture_root_does_not_own_source_build_recipe_authority() -> None:
    payload = json.loads(OVERLAY.read_text(encoding="utf-8"))
    source_entries = [entry for entry in payload["entries"] if entry["schema_id"] != "synergy.service-build-recipe-registry/v1"]
    assert all(entry["producer"] != "Shtenco/synergy_system" for entry in source_entries)
    assert all(entry["authority"] == "SOURCE_BUILD_RECIPE_ONLY" for entry in source_entries)
