from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

from synergy_system.node_build_plan_v1 import (
    NodeBuildPlanError,
    plan_digest,
    verify_research_node_build_plan_context_v1,
    verify_research_node_build_plan_v1,
)


ROOT = Path(__file__).resolve().parents[1]


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text())


def _plan() -> dict:
    return _load("fixtures/node_build_plans/research_compute_node_build_plan_source_candidate_v1.json")


def _lock() -> dict:
    return _load("fixtures/node_build_locks/research_compute_node_source_candidate_v1.json")


def _recipes() -> dict[str, dict]:
    return {
        "Shtenco/agi_nexus": _load("fixtures/build_recipes/agi_nexus_build_recipe_v1.json"),
        "Shtenco/synergynet": _load("fixtures/build_recipes/synergynet_build_recipe_v1.json"),
    }


def test_plan_verifies_schema_and_cross_root_context() -> None:
    plan = _plan()
    assert verify_research_node_build_plan_v1(plan) == plan
    assert verify_research_node_build_plan_context_v1(plan, _lock(), _recipes()) == plan
    schema = _load("schemas/synergy_node_build_plan_v1.schema.json")
    jsonschema.validate(plan, schema)


def test_fresh_plan_hash_cannot_claim_artifacts_or_reproducibility() -> None:
    plan = copy.deepcopy(_plan())
    plan["services"][0]["build_artifact_digest"] = "aa" * 32
    plan["services"][0]["reproducibility_status"] = "REPRODUCIBLE"
    plan["plan_status"] = "BUILD_VERIFIED"
    plan["plan_digest"] = plan_digest(plan)
    with pytest.raises(NodeBuildPlanError):
        verify_research_node_build_plan_v1(plan)


def test_changed_recipe_bytes_with_old_digest_are_rejected() -> None:
    recipes = _recipes()
    recipes["Shtenco/agi_nexus"] = copy.deepcopy(recipes["Shtenco/agi_nexus"])
    recipes["Shtenco/agi_nexus"]["python_requires"] = ">=3.12"
    with pytest.raises(NodeBuildPlanError):
        verify_research_node_build_plan_context_v1(_plan(), _lock(), recipes)


def test_self_consistent_stronger_recipe_is_still_wrong_generation() -> None:
    recipes = _recipes()
    recipe = copy.deepcopy(recipes["Shtenco/synergynet"])
    recipe["build_toolchain"] = {"status": "FROZEN", "lock_digest": "ab" * 32}
    recipe["reproducibility_status"] = "REPRODUCIBLE"
    recipe["artifact_digest"] = "cd" * 32
    body = dict(recipe)
    body.pop("recipe_digest", None)
    import hashlib
    from synergy_system.node_build_plan_v1 import _canonical

    recipe["recipe_digest"] = hashlib.sha256(_canonical(body)).hexdigest()
    recipes["Shtenco/synergynet"] = recipe
    with pytest.raises(NodeBuildPlanError):
        verify_research_node_build_plan_context_v1(_plan(), _lock(), recipes)


def test_source_lock_bytes_must_match_declared_digest() -> None:
    source_lock = copy.deepcopy(_lock())
    source_lock["services"][0]["source_ref"] = "different-ref"
    with pytest.raises(NodeBuildPlanError):
        verify_research_node_build_plan_context_v1(_plan(), source_lock, _recipes())
