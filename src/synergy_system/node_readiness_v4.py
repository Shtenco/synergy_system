from __future__ import annotations

import hashlib
import json
from typing import Any

from .node_readiness_v3 import verify_source_revision_v2


class NodeReadinessV4Error(ValueError):
    pass

PROFILE = "406740705e853fa51ad4eacf7a01925fbe4b5cec491be35ea12ba777d217d714"
BASE_LOCK = "14c763218602585d49e12060e1e6cf21d33815fda0cb18711a6522a26157ace2"
REVISION = "82d4b40e2276b8095f7fd3ff2105181d9c038b3e2879265facd022ff30d9fb32"
PREV_PLAN = "5ac2d5a20428d5e3f88bf25b52137177122cb7d0d3feebf62efeb0576aedddd2"
PLAN = "8f37d84645e78818b17c884e7c46d1ba680e79a53a2125faab64de42a290953f"
PREV_READINESS = "2d2622e82f0a818facdc46a2fac0773107d42b8d8e7b519b4d2fe4030efd1a89"
READINESS = "ee20353d76d377f31f8054dae0c6463db4b3aae1a57b4ccfc2d7631e2251a95b"
TOOLCHAIN = "af92c9f1909ae3b64aaea78bdce2c6d05deb974ad242482b36e0c8ce820a2848"
BUILDER = "5fe5d1e8b8e12d1c6408590e93d3e5abe1a208d921ae20066c45a813e036eaed"
ARTIFACT_SET = "14a67cfbe75361a8ca2f3bd43befd3aef97eddc29d4d725bd83f289ed829bc77"

DOMAIN = {
    "content-cache": {"repo":"Shtenco/synergynet","recipe":"37cb503fb8c6d5e8ef2305ce03d0332abee2d9eed5bb29f90364e20874d128df","evidence":"8c4f44f1b0b95221d660bb4a7c0598ada17e86f59bade16e85d93789bf1ddd8c","artifact":"7f22e68d80a7df879af71ebccdb45f8edb10cae3698bf07faa7076ce76fd0ef7","runtime":"abb35edd0336ea36f249d24b04e1b7482fea4ecebc5c881b655bf8a390d8b5ad"},
    "nexus": {"repo":"Shtenco/agi_nexus","recipe":"3bbe2bf1f90a9ed1abade80782062256a1a72619b72345da41f7ed9897b4a735","evidence":"cd14275a264ec1f0ef7045721eb18e31787d918cd78563f93ebb486333f8daee","artifact":"fa7bbd141566d1542a5c03ee485de8ebd5f2ed76557ac56ff728196429fbbb64","runtime":"376f6a85fb1ddb2abe529559b73964241fb3f25a2a8832657eb0f19a1ecc6738"},
    "synergynet": {"repo":"Shtenco/synergynet","recipe":"37cb503fb8c6d5e8ef2305ce03d0332abee2d9eed5bb29f90364e20874d128df","evidence":"8c4f44f1b0b95221d660bb4a7c0598ada17e86f59bade16e85d93789bf1ddd8c","artifact":"7f22e68d80a7df879af71ebccdb45f8edb10cae3698bf07faa7076ce76fd0ef7","runtime":"8c38cd130e3dd73723e3a3241d2df61bef218abdab2d16785ccec5b172fac4df"},
}


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(payload: dict[str, Any], self_field: str) -> str:
    body = dict(payload); body.pop(self_field, None)
    return hashlib.sha256(canonical(body)).hexdigest()


def require_digest(payload: dict[str, Any], field: str, expected: str) -> None:
    if payload.get(field) != expected or digest(payload, field) != expected:
        raise NodeReadinessV4Error(f"{field} mismatch")


def verify_toolchain(lock: dict[str, Any]) -> None:
    if lock.get("schema") != "synergy.build-toolchain-lock/v1" or lock.get("lock_digest") != TOOLCHAIN:
        raise NodeReadinessV4Error("toolchain identity drifted")
    if digest(lock, "lock_digest") != TOOLCHAIN:
        raise NodeReadinessV4Error("toolchain self digest mismatch")
    if lock.get("builder", {}).get("sha256") != BUILDER:
        raise NodeReadinessV4Error("builder drifted")
    if lock.get("network_required_to_build") is not False or lock.get("setuptools_required_to_build") is not False or lock.get("wheel_required_to_build") is not False:
        raise NodeReadinessV4Error("toolchain dependency drifted")
    if lock.get("execution_authority") != "NONE":
        raise NodeReadinessV4Error("toolchain authority escalation")


def verify_recipe(recipe: dict[str, Any], sid: str) -> None:
    exp = DOMAIN[sid]
    if recipe.get("schema") != "synergy.build-recipe/v3" or recipe.get("repository") != exp["repo"]:
        raise NodeReadinessV4Error(f"{sid} recipe identity drifted")
    require_digest(recipe, "recipe_digest", exp["recipe"])
    if recipe.get("toolchain_lock_digest") != TOOLCHAIN or recipe.get("builder_sha256") != BUILDER:
        raise NodeReadinessV4Error(f"{sid} recipe toolchain drifted")
    if recipe.get("artifact_digest") != exp["artifact"] or recipe.get("artifact_kind") != "PYTHON_ZIPAPP_ZIP_STORED":
        raise NodeReadinessV4Error(f"{sid} recipe artifact drifted")
    if recipe.get("reproducibility_status") != "REPRODUCIBLE_BYTE_IDENTICAL" or recipe.get("runtime_requirements") != []:
        raise NodeReadinessV4Error(f"{sid} reproducibility overclaim")
    if recipe.get("execution_authority") != "NONE":
        raise NodeReadinessV4Error(f"{sid} recipe authority escalation")


def verify_evidence(evidence: dict[str, Any], recipe: dict[str, Any], sid: str) -> None:
    exp = DOMAIN[sid]
    if evidence.get("schema") != "synergy.build-evidence/v1" or evidence.get("repository") != exp["repo"]:
        raise NodeReadinessV4Error(f"{sid} evidence identity drifted")
    require_digest(evidence, "evidence_digest", exp["evidence"])
    if evidence.get("recipe_digest") != exp["recipe"] or evidence.get("toolchain_lock_digest") != TOOLCHAIN or evidence.get("builder_sha256") != BUILDER:
        raise NodeReadinessV4Error(f"{sid} evidence binding drifted")
    builds = evidence.get("builds")
    if evidence.get("build_count") != 2 or not isinstance(builds, list) or len(builds) != 2:
        raise NodeReadinessV4Error(f"{sid} repeated-build evidence missing")
    if evidence.get("byte_identical") is not True:
        raise NodeReadinessV4Error(f"{sid} builds are not byte-identical")
    for build in builds:
        if build.get("artifact_digest") != exp["artifact"] or build.get("artifact_size") != recipe.get("artifact_size"):
            raise NodeReadinessV4Error(f"{sid} build output drifted")
    tests = evidence.get("executed_smoke_tests")
    if not isinstance(tests, list) or not tests or any(x.get("status") != "PASS" for x in tests):
        raise NodeReadinessV4Error(f"{sid} artifact smoke evidence incomplete")
    if evidence.get("artifact_status") != "VERIFIED_EXECUTABLE" or evidence.get("execution_authority") != "NONE":
        raise NodeReadinessV4Error(f"{sid} artifact evidence status/authority drifted")


def verify_runtime_spec(spec: dict[str, Any], sid: str) -> None:
    exp=DOMAIN[sid]
    if spec.get("schema") != "synergy.artifact-runtime-spec/v1" or spec.get("service_id") != sid or spec.get("repository") != exp["repo"]:
        raise NodeReadinessV4Error(f"{sid} runtime spec identity drifted")
    require_digest(spec, "runtime_spec_digest", exp["runtime"])
    if spec.get("artifact_digest") != exp["artifact"] or spec.get("artifact_kind") != "PYTHON_ZIPAPP_ZIP_STORED":
        raise NodeReadinessV4Error(f"{sid} runtime artifact drifted")
    if spec.get("execution_authority") != "NONE" or spec.get("remote_filesystem_path_authority") != "NONE":
        raise NodeReadinessV4Error(f"{sid} runtime authority escalation")
    if sid == "nexus" and (spec.get("network_access") != "NONE" or spec.get("process_execution_authority") != "NONE" or spec.get("financial_authority") != "NONE"):
        raise NodeReadinessV4Error("NEXUS authority escalation")


def derived_build_blockers(lock, recipes, evidence, runtime_specs) -> list[str]:
    try:
        verify_toolchain(lock)
    except NodeReadinessV4Error:
        return ["BUILD_TOOLCHAIN_NOT_FROZEN"]
    try:
        for sid in ("content-cache", "nexus", "synergynet"):
            verify_recipe(recipes[sid], sid)
            verify_evidence(evidence[sid], recipes[sid], sid)
            verify_runtime_spec(runtime_specs[sid], sid)
    except NodeReadinessV4Error:
        return ["BUILD_ARTIFACTS_NOT_VERIFIED"]
    return []


def verify_build_plan_v4(plan, revision, lock, recipes, evidence, runtime_specs):
    verify_source_revision_v2(revision)
    blockers=derived_build_blockers(lock, recipes, evidence, runtime_specs)
    if plan.get("schema") != "synergy.node-build-plan/v4" or plan.get("profile_digest") != PROFILE or plan.get("base_source_lock_digest") != BASE_LOCK:
        raise NodeReadinessV4Error("build plan root drifted")
    if plan.get("source_revision_digest") != REVISION or plan.get("previous_build_plan_digest") != PREV_PLAN or plan.get("toolchain_lock_digest") != TOOLCHAIN:
        raise NodeReadinessV4Error("build plan ancestry/toolchain drifted")
    services=plan.get("services")
    if not isinstance(services,list) or [x.get("service_id") for x in services] != ["content-cache","nexus","synergynet"]:
        raise NodeReadinessV4Error("build plan service set drifted")
    artifact_map={}
    for item in services:
        sid=item["service_id"]; exp=DOMAIN[sid]; artifact_map[sid]=exp["artifact"]
        expected={"repository":exp["repo"],"build_recipe_digest":exp["recipe"],"build_evidence_digest":exp["evidence"],"artifact_digest":exp["artifact"],"artifact_runtime_spec_digest":exp["runtime"],"reproducibility_status":"REPRODUCIBLE_BYTE_IDENTICAL","artifact_status":"VERIFIED_EXECUTABLE","execution_authority":"NONE"}
        for key,val in expected.items():
            if item.get(key)!=val: raise NodeReadinessV4Error(f"{sid} plan binding drifted: {key}")
    aset=hashlib.sha256(canonical(artifact_map)).hexdigest()
    if plan.get("artifact_set_digest") != aset or aset != ARTIFACT_SET:
        raise NodeReadinessV4Error("artifact set digest drifted")
    if plan.get("build_blockers") != blockers:
        raise NodeReadinessV4Error("build blockers are not evidence-derived")
    expected_status="BUILD_ARTIFACTS_VERIFIED_REPRODUCIBLE" if not blockers else "BUILD_PLAN_BLOCKED"
    if plan.get("plan_status") != expected_status or plan.get("execution_authority") != "NONE":
        raise NodeReadinessV4Error("build plan status/authority drifted")
    require_digest(plan,"plan_digest",PLAN)
    return plan


def verify_readiness_v4(readiness, plan, revision, lock, recipes, evidence, runtime_specs):
    verify_build_plan_v4(plan, revision, lock, recipes, evidence, runtime_specs)
    blockers=list(plan["build_blockers"])
    if readiness.get("schema") != "synergy.node-readiness/v4" or readiness.get("previous_readiness_digest") != PREV_READINESS:
        raise NodeReadinessV4Error("readiness ancestry drifted")
    for field,expected in (("profile_digest",PROFILE),("base_source_lock_digest",BASE_LOCK),("source_revision_digest",REVISION),("build_plan_digest",PLAN),("toolchain_lock_digest",TOOLCHAIN),("artifact_set_digest",ARTIFACT_SET)):
        if readiness.get(field)!=expected: raise NodeReadinessV4Error(f"readiness {field} drifted")
    if readiness.get("blockers") != blockers:
        raise NodeReadinessV4Error("readiness blockers are not evidence-derived")
    if blockers:
        raise NodeReadinessV4Error("v4 fixture cannot be admission-ready with blockers")
    if readiness.get("resolved_since_v3") != ["BUILD_ARTIFACTS_NOT_VERIFIED","BUILD_TOOLCHAIN_NOT_FROZEN"]:
        raise NodeReadinessV4Error("resolved blocker ancestry drifted")
    if readiness.get("build_status") != "BUILD_ARTIFACTS_VERIFIED_REPRODUCIBLE" or readiness.get("service_status") != "ALL_REQUIRED_SERVICES_ARTIFACT_VERIFIED":
        raise NodeReadinessV4Error("readiness verified status drifted")
    if readiness.get("node_status") != "NODE_ADMISSION_READY_NOT_RUNNING" or readiness.get("auto_start") is not False or readiness.get("execution_authority") != "NONE":
        raise NodeReadinessV4Error("readiness cannot start or authorize node")
    require_digest(readiness,"readiness_digest",READINESS)
    return readiness
