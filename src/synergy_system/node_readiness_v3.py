from __future__ import annotations

import hashlib
import json
from typing import Any


class NodeReadinessV3Error(ValueError):
    pass


PROFILE = "406740705e853fa51ad4eacf7a01925fbe4b5cec491be35ea12ba777d217d714"
BASE_LOCK = "14c763218602585d49e12060e1e6cf21d33815fda0cb18711a6522a26157ace2"
PREV_REVISION = "3baac7cb6277e1d73110f7acf35de464233c8debfc1e5a3b0f595de303369d21"
REVISION = "82d4b40e2276b8095f7fd3ff2105181d9c038b3e2879265facd022ff30d9fb32"
PREV_PLAN = "1993b95cb0b41584429c35f432f8a10d35a21dd72381e2f7821515769556e2b3"
PLAN = "5ac2d5a20428d5e3f88bf25b52137177122cb7d0d3feebf62efeb0576aedddd2"
PREV_READINESS = "b590134ce5c6246bd686ff3bf3678a5ffc75524e7034f5dfdc14587cbfe16994"
READINESS = "2d2622e82f0a818facdc46a2fac0773107d42b8d8e7b519b4d2fe4030efd1a89"
NEXUS_RUNTIME = "4915872c60117bbac0001a0f792f2a8f3a12899a"
NEXUS_BUILD_SOURCE = "0cf581fe6ac6e79bcf39c9ed4833e2d5719ddd6f"
NEXUS_SPEC = "c01a22e4dbd5a1e4e6f2b9a3fbc9e49f559a43f1575cd4e6a6f4c22420f3121b"
NEXUS_RECIPE = "46e874b075c52ee81e4996c6ce3fc027078f54ad4c4824a869d92b597821fe90"
SYNERGYNET_RUNTIME = "aa93e18bdeb84a8475419cde83f149c8381428cd"
SYNERGYNET_BUILD = "d2f5256825f4ee3e878476556a427b3172cf5d31"
CONTENT_SPEC = "5ace3018df97985f12d4c28da619b0598223eab34a710cac37d32edaf42ab1fd"
RELAY_SPEC = "42c8b0df5e55345bd6b6636dfd4fd311035bd2bca91a9613814beeac08984fce"
SYNERGYNET_RECIPE = "9760d89fbc1de9553052db07feee7819bedee98aa0688efcabae7415aa143565"


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(payload: dict[str, Any], self_field: str) -> str:
    body = dict(payload)
    body.pop(self_field, None)
    return hashlib.sha256(canonical(body)).hexdigest()


def require_self_digest(payload: dict[str, Any], field: str, expected: str) -> None:
    if payload.get(field) != expected or digest(payload, field) != expected:
        raise NodeReadinessV3Error(f"{field} mismatch")


def verify_nexus_service_spec_v2(spec: dict[str, Any]) -> dict[str, Any]:
    expected = {
        "schema": "synergy.service-spec/v2",
        "service_id": "nexus",
        "kind": "NEXUS",
        "repository": "Shtenco/agi_nexus",
        "runtime_source_commit": NEXUS_RUNTIME,
        "r710_freeze_commit": "fc8a32bc949947a42ab5038de0a3e55fa9921e64",
        "required_capabilities": ["NEXUS_COMPUTE"],
        "runtime_form": "PYTHON_STDLIB_SERVICE",
        "entrypoint": "python -m agi_nexus.nexus_service_v3",
        "health_probe": "STATUS_EXPECT_READY",
        "lifecycle_protocol": "STDIN_EOF_OR_SUPERVISOR_SIGNAL",
        "wire_protocol": "nexus.runtime-wire/v3",
        "operations": ["STATUS", "FORMAL_REASON", "SMALLWORLD_EXACT_DIGESTS", "CYBER_STEP"],
        "interface_status": "SERVICE_INTERFACE_IMPLEMENTED_SOURCE_ONLY",
        "neural_hypothesis_status": "NOT_MIGRATED_NOT_REQUIRED_FOR_EXACT_CORE",
        "build_artifact_digest": None,
        "build_evidence_digest": None,
        "execution_authority": "NONE",
    }
    if not isinstance(spec, dict) or set(spec) != set(expected) | {"spec_digest"}:
        raise NodeReadinessV3Error("unexpected NEXUS ServiceSpec shape")
    for key, value in expected.items():
        if spec[key] != value:
            raise NodeReadinessV3Error(f"NEXUS ServiceSpec {key} drifted")
    require_self_digest(spec, "spec_digest", NEXUS_SPEC)
    return spec


def verify_nexus_build_recipe_v2(recipe: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    verify_nexus_service_spec_v2(spec)
    expected = {
        "schema": "synergy.build-recipe/v2",
        "recipe_id": "AGI_NEXUS_PROOF_CORE_SOURCE_CANDIDATE_20260822",
        "repository": "Shtenco/agi_nexus",
        "source_commit": NEXUS_BUILD_SOURCE,
        "source_role": "NEXUS_PROOF_FIRST_MINIMAL_CORE_V3",
        "service_spec_digest": NEXUS_SPEC,
        "artifact_kind": "PYTHON_WHEEL",
        "package_name": "agi-nexus",
        "package_version": "0.1.0",
        "python_requires": ">=3.11",
        "build_backend": "setuptools.build_meta",
        "build_system_requirements": ["setuptools>=68"],
        "runtime_requirements": [],
        "build_toolchain": {"status": "NOT_FROZEN", "lock_digest": None},
        "reproducibility_status": "NOT_REPRODUCIBLE_TOOLCHAIN_NOT_FROZEN",
        "artifact_digest": None,
        "build_evidence_digest": None,
        "execution_authority": "NONE",
    }
    if not isinstance(recipe, dict) or set(recipe) != set(expected) | {"recipe_digest"}:
        raise NodeReadinessV3Error("unexpected NEXUS BuildRecipe shape")
    for key, value in expected.items():
        if recipe[key] != value:
            raise NodeReadinessV3Error(f"NEXUS BuildRecipe {key} drifted")
    require_self_digest(recipe, "recipe_digest", NEXUS_RECIPE)
    return recipe


def verify_source_revision_v2(revision: dict[str, Any]) -> dict[str, Any]:
    if revision.get("schema") != "synergy.node-source-revision/v2":
        raise NodeReadinessV3Error("wrong source revision schema")
    if revision.get("profile_digest") != PROFILE or revision.get("base_source_lock_digest") != BASE_LOCK:
        raise NodeReadinessV3Error("source revision root binding drifted")
    if revision.get("previous_source_revision_digest") != PREV_REVISION:
        raise NodeReadinessV3Error("source revision ancestry drifted")
    services = revision.get("services")
    if not isinstance(services, list) or [x.get("service_id") for x in services] != ["content-cache", "nexus", "synergynet"]:
        raise NodeReadinessV3Error("source revision service set drifted")
    expected = {
        "content-cache": ("Shtenco/synergynet", SYNERGYNET_RUNTIME, SYNERGYNET_BUILD, CONTENT_SPEC, "UNCHANGED"),
        "nexus": ("Shtenco/agi_nexus", NEXUS_RUNTIME, NEXUS_BUILD_SOURCE, NEXUS_SPEC, "UPDATED"),
        "synergynet": ("Shtenco/synergynet", SYNERGYNET_RUNTIME, SYNERGYNET_BUILD, RELAY_SPEC, "UNCHANGED"),
    }
    for item in services:
        repo, runtime, build, spec, revision_kind = expected[item["service_id"]]
        if item.get("repository") != repo or item.get("runtime_source_commit") != runtime or item.get("build_source_commit") != build:
            raise NodeReadinessV3Error("source identity drifted")
        if item.get("service_spec_digest") != spec or item.get("revision_kind") != revision_kind:
            raise NodeReadinessV3Error("source revision evidence drifted")
        if item.get("interface_status") != "SERVICE_INTERFACE_IMPLEMENTED_SOURCE_ONLY":
            raise NodeReadinessV3Error("all v3 service interfaces must be source-implemented")
    if revision.get("revision_status") != "SOURCE_REVISION_FROZEN_BUILD_NOT_VERIFIED" or revision.get("execution_authority") != "NONE":
        raise NodeReadinessV3Error("source revision status/authority drifted")
    require_self_digest(revision, "revision_digest", REVISION)
    return revision


def verify_build_plan_v3(plan: dict[str, Any], revision: dict[str, Any], nexus_recipe: dict[str, Any], nexus_spec: dict[str, Any]) -> dict[str, Any]:
    verify_source_revision_v2(revision)
    verify_nexus_build_recipe_v2(nexus_recipe, nexus_spec)
    if plan.get("schema") != "synergy.node-build-plan/v3":
        raise NodeReadinessV3Error("wrong build plan schema")
    if plan.get("profile_digest") != PROFILE or plan.get("base_source_lock_digest") != BASE_LOCK:
        raise NodeReadinessV3Error("build plan root binding drifted")
    if plan.get("source_revision_digest") != REVISION or plan.get("previous_build_plan_digest") != PREV_PLAN:
        raise NodeReadinessV3Error("build plan ancestry/evidence drifted")
    services = plan.get("services")
    if not isinstance(services, list) or [x.get("service_id") for x in services] != ["content-cache", "nexus", "synergynet"]:
        raise NodeReadinessV3Error("build plan service set drifted")
    recipes = {"content-cache": SYNERGYNET_RECIPE, "nexus": NEXUS_RECIPE, "synergynet": SYNERGYNET_RECIPE}
    specs = {"content-cache": CONTENT_SPEC, "nexus": NEXUS_SPEC, "synergynet": RELAY_SPEC}
    for item in services:
        sid = item["service_id"]
        if item.get("service_spec_digest") != specs[sid] or item.get("build_recipe_digest") != recipes[sid]:
            raise NodeReadinessV3Error("plan domain evidence drifted")
        if item.get("interface_status") != "SERVICE_INTERFACE_IMPLEMENTED_SOURCE_ONLY":
            raise NodeReadinessV3Error("plan contains incomplete service interface")
        if item.get("reproducibility_status") != "NOT_REPRODUCIBLE_TOOLCHAIN_NOT_FROZEN":
            raise NodeReadinessV3Error("plan reproducibility overclaim")
        if item.get("build_artifact_digest") is not None or item.get("build_evidence_digest") is not None:
            raise NodeReadinessV3Error("plan build evidence overclaim")
    if plan.get("build_blockers") != ["BUILD_ARTIFACTS_NOT_VERIFIED", "BUILD_TOOLCHAIN_NOT_FROZEN"]:
        raise NodeReadinessV3Error("build blocker set drifted")
    if plan.get("plan_status") != "BUILD_PLAN_NOT_REPRODUCIBLE_YET" or plan.get("execution_authority") != "NONE":
        raise NodeReadinessV3Error("build plan status/authority drifted")
    require_self_digest(plan, "plan_digest", PLAN)
    return plan


def verify_readiness_v3(readiness: dict[str, Any], plan: dict[str, Any], revision: dict[str, Any], nexus_recipe: dict[str, Any], nexus_spec: dict[str, Any]) -> dict[str, Any]:
    verify_build_plan_v3(plan, revision, nexus_recipe, nexus_spec)
    if readiness.get("schema") != "synergy.node-readiness/v3":
        raise NodeReadinessV3Error("wrong readiness schema")
    if readiness.get("previous_readiness_digest") != PREV_READINESS:
        raise NodeReadinessV3Error("readiness ancestry drifted")
    if readiness.get("profile_digest") != PROFILE or readiness.get("base_source_lock_digest") != BASE_LOCK:
        raise NodeReadinessV3Error("readiness root binding drifted")
    if readiness.get("source_revision_digest") != REVISION or readiness.get("build_plan_digest") != PLAN:
        raise NodeReadinessV3Error("readiness evidence drifted")
    derived_service_blockers = [
        f"{item['service_id'].upper().replace('-', '_')}_SERVICE_INTERFACE_NOT_IMPLEMENTED"
        for item in revision["services"]
        if item["interface_status"] != "SERVICE_INTERFACE_IMPLEMENTED_SOURCE_ONLY"
    ]
    derived_blockers = sorted(["BUILD_ARTIFACTS_NOT_VERIFIED", "BUILD_TOOLCHAIN_NOT_FROZEN"] + derived_service_blockers)
    if readiness.get("blockers") != derived_blockers:
        raise NodeReadinessV3Error("readiness blockers are not evidence-derived")
    if derived_service_blockers:
        raise NodeReadinessV3Error("v3 must have all required service interfaces implemented")
    if readiness.get("resolved_since_v2") != ["NEXUS_SERVICE_INTERFACE_NOT_IMPLEMENTED"]:
        raise NodeReadinessV3Error("resolved blocker ancestry drifted")
    if readiness.get("service_status") != "ALL_REQUIRED_SERVICE_INTERFACES_IMPLEMENTED_SOURCE_ONLY":
        raise NodeReadinessV3Error("service status drifted")
    if readiness.get("build_status") != "BUILD_PLAN_NOT_REPRODUCIBLE_YET":
        raise NodeReadinessV3Error("build status drifted")
    if readiness.get("node_status") != "NODE_NOT_DEPLOYABLE" or readiness.get("execution_authority") != "NONE":
        raise NodeReadinessV3Error("readiness cannot grant deployment/execution")
    require_self_digest(readiness, "readiness_digest", READINESS)
    return readiness
