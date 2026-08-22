from __future__ import annotations

import hashlib
import json
from typing import Any


class NodeReadinessV2Error(ValueError):
    pass


_PROFILE = "406740705e853fa51ad4eacf7a01925fbe4b5cec491be35ea12ba777d217d714"
_BASE_LOCK = "14c763218602585d49e12060e1e6cf21d33815fda0cb18711a6522a26157ace2"
_PREVIOUS_READINESS = "39a3405b4e5da9b79b260f67f9ec975433ed171d8801eb55edc648b1f38370d8"
_REVISION_DIGEST = "3baac7cb6277e1d73110f7acf35de464233c8debfc1e5a3b0f595de303369d21"
_PLAN_DIGEST = "1993b95cb0b41584429c35f432f8a10d35a21dd72381e2f7821515769556e2b3"
_READINESS_DIGEST = "b590134ce5c6246bd686ff3bf3678a5ffc75524e7034f5dfdc14587cbfe16994"
_RUNTIME_SOURCE = "aa93e18bdeb84a8475419cde83f149c8381428cd"
_BUILD_SOURCE = "d2f5256825f4ee3e878476556a427b3172cf5d31"
_NEXUS_SOURCE = "cbc06e83f7f9e242719667e446a090894e11eef1"
_SERVICE_SPEC_DIGESTS = {
    "content-cache": "5ace3018df97985f12d4c28da619b0598223eab34a710cac37d32edaf42ab1fd",
    "nexus": "ab83e935b2cdd2eb855737a18f4e8e039ebb166cfe431d8d1652a44a63af522d",
    "synergynet": "42c8b0df5e55345bd6b6636dfd4fd311035bd2bca91a9613814beeac08984fce",
}
_BUILD_RECIPE_DIGESTS = {
    "content-cache": "9760d89fbc1de9553052db07feee7819bedee98aa0688efcabae7415aa143565",
    "nexus": "b262c98666843da80f37bcfae4d8b2105aa3b52b758a3a50406b198afc1a15be",
    "synergynet": "9760d89fbc1de9553052db07feee7819bedee98aa0688efcabae7415aa143565",
}
_V1_BLOCKERS = {
    "BUILD_ARTIFACTS_NOT_VERIFIED",
    "BUILD_TOOLCHAIN_NOT_FROZEN",
    "CONTENT_CACHE_SERVICE_INTERFACE_NOT_IMPLEMENTED",
    "NEXUS_SERVICE_INTERFACE_NOT_IMPLEMENTED",
    "SYNERGYNET_SERVICE_INTERFACE_NOT_IMPLEMENTED",
}


def _canonical(value: Any) -> bytes:
    def check(item: Any) -> None:
        if item is None or isinstance(item, (str, bool)):
            return
        if isinstance(item, int) and not isinstance(item, bool):
            if abs(item) > 2**53 - 1:
                raise NodeReadinessV2Error("unsafe integer")
            return
        if isinstance(item, float):
            raise NodeReadinessV2Error("floating point values are forbidden")
        if isinstance(item, list):
            for child in item:
                check(child)
            return
        if isinstance(item, dict):
            if any(not isinstance(key, str) for key in item):
                raise NodeReadinessV2Error("object keys must be strings")
            for child in item.values():
                check(child)
            return
        raise NodeReadinessV2Error("unsupported value")

    check(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _digest(payload: dict[str, Any], self_field: str | None = None) -> str:
    body = dict(payload)
    if self_field is not None:
        body.pop(self_field, None)
    return hashlib.sha256(_canonical(body)).hexdigest()


def _expect_digest(payload: dict[str, Any], field: str, expected: str) -> None:
    if payload.get(field) != expected or _digest(payload, field) != expected:
        raise NodeReadinessV2Error(f"{field} mismatch")


def _verify_service_specs(
    nexus_spec: dict[str, Any],
    content_spec: dict[str, Any],
    relay_spec: dict[str, Any],
) -> None:
    if nexus_spec.get("schema") != "synergy.service-spec/v1" or nexus_spec.get("service_id") != "nexus":
        raise NodeReadinessV2Error("wrong NEXUS ServiceSpec")
    if nexus_spec.get("source_commit") != _NEXUS_SOURCE:
        raise NodeReadinessV2Error("NEXUS ServiceSpec source drifted")
    if nexus_spec.get("readiness_status") != "SERVICE_INTERFACE_NOT_IMPLEMENTED":
        raise NodeReadinessV2Error("NEXUS interface status drifted")
    if nexus_spec.get("execution_authority") != "NONE":
        raise NodeReadinessV2Error("NEXUS ServiceSpec grants authority")
    _expect_digest(nexus_spec, "spec_digest", _SERVICE_SPEC_DIGESTS["nexus"])

    expected = {
        "content-cache": (content_spec, "CONTENT_CACHE", "synergynet.content-wire/v2", "python -m synergynet.content_service_v2"),
        "synergynet": (relay_spec, "SYNERGYNET", "synergynet.relay-wire/v2", "python -m synergynet.relay_service_v2"),
    }
    for service_id, (spec, kind, wire, entrypoint) in expected.items():
        if spec.get("schema") != "synergy.service-spec/v2" or spec.get("service_id") != service_id:
            raise NodeReadinessV2Error("wrong SynergyNet ServiceSpec identity")
        if spec.get("kind") != kind or spec.get("repository") != "Shtenco/synergynet":
            raise NodeReadinessV2Error("SynergyNet ServiceSpec ownership drifted")
        if spec.get("source_commit") != _RUNTIME_SOURCE:
            raise NodeReadinessV2Error("runtime source commit drifted")
        if spec.get("runtime_form") != "PYTHON_SERVICE" or spec.get("entrypoint") != entrypoint:
            raise NodeReadinessV2Error("runtime entrypoint drifted")
        if spec.get("health_probe") != "STATUS_EXPECT_READY":
            raise NodeReadinessV2Error("health contract drifted")
        if spec.get("lifecycle_protocol") != "SIGINT_SIGTERM_GRACEFUL_SHUTDOWN":
            raise NodeReadinessV2Error("lifecycle contract drifted")
        if spec.get("wire_protocol") != wire:
            raise NodeReadinessV2Error("wire protocol drifted")
        if spec.get("interface_status") != "SERVICE_INTERFACE_IMPLEMENTED_SOURCE_ONLY":
            raise NodeReadinessV2Error("SynergyNet interface status drifted")
        if spec.get("build_artifact_digest") is not None or spec.get("build_evidence_digest") is not None:
            raise NodeReadinessV2Error("ServiceSpec cannot claim build evidence")
        if spec.get("execution_authority") != "NONE":
            raise NodeReadinessV2Error("ServiceSpec grants execution authority")
        _expect_digest(spec, "spec_digest", _SERVICE_SPEC_DIGESTS[service_id])


def _verify_build_recipes(nexus_recipe: dict[str, Any], synergynet_recipe: dict[str, Any]) -> None:
    if nexus_recipe.get("schema") != "synergy.build-recipe/v1":
        raise NodeReadinessV2Error("wrong NEXUS BuildRecipe schema")
    if nexus_recipe.get("source_commit") != _NEXUS_SOURCE:
        raise NodeReadinessV2Error("NEXUS recipe source drifted")
    if nexus_recipe.get("build_toolchain") != {"status": "NOT_FROZEN", "lock_digest": None}:
        raise NodeReadinessV2Error("NEXUS toolchain state drifted")
    if nexus_recipe.get("artifact_digest") is not None:
        raise NodeReadinessV2Error("NEXUS artifact overclaim")
    if nexus_recipe.get("execution_authority") != "NONE":
        raise NodeReadinessV2Error("NEXUS recipe grants authority")
    _expect_digest(nexus_recipe, "recipe_digest", _BUILD_RECIPE_DIGESTS["nexus"])

    if synergynet_recipe.get("schema") != "synergy.build-recipe/v2":
        raise NodeReadinessV2Error("wrong SynergyNet BuildRecipe schema")
    if synergynet_recipe.get("source_commit") != _BUILD_SOURCE:
        raise NodeReadinessV2Error("SynergyNet build source drifted")
    if synergynet_recipe.get("service_spec_digests") != {
        "content-cache": _SERVICE_SPEC_DIGESTS["content-cache"],
        "synergynet": _SERVICE_SPEC_DIGESTS["synergynet"],
    }:
        raise NodeReadinessV2Error("SynergyNet recipe ServiceSpec binding drifted")
    if synergynet_recipe.get("build_toolchain") != {"status": "NOT_FROZEN", "lock_digest": None}:
        raise NodeReadinessV2Error("SynergyNet toolchain state drifted")
    if synergynet_recipe.get("artifact_digest") is not None or synergynet_recipe.get("build_evidence_digest") is not None:
        raise NodeReadinessV2Error("SynergyNet artifact/evidence overclaim")
    if synergynet_recipe.get("execution_authority") != "NONE":
        raise NodeReadinessV2Error("SynergyNet recipe grants authority")
    _expect_digest(synergynet_recipe, "recipe_digest", _BUILD_RECIPE_DIGESTS["synergynet"])


def verify_source_revision_v1(revision: dict[str, Any]) -> dict[str, Any]:
    if revision.get("schema") != "synergy.node-source-revision/v1":
        raise NodeReadinessV2Error("wrong source revision schema")
    if revision.get("profile_digest") != _PROFILE or revision.get("base_source_lock_digest") != _BASE_LOCK:
        raise NodeReadinessV2Error("source revision root binding drifted")
    if revision.get("revision_status") != "SOURCE_REVISION_FROZEN_BUILD_NOT_VERIFIED":
        raise NodeReadinessV2Error("source revision status drifted")
    if revision.get("execution_authority") != "NONE":
        raise NodeReadinessV2Error("source revision grants authority")
    services = revision.get("services")
    if not isinstance(services, list) or [item.get("service_id") for item in services] != ["content-cache", "nexus", "synergynet"]:
        raise NodeReadinessV2Error("source revision service set drifted")
    for item in services:
        service_id = item["service_id"]
        if item.get("service_spec_digest") != _SERVICE_SPEC_DIGESTS[service_id]:
            raise NodeReadinessV2Error("source revision ServiceSpec drifted")
        if service_id == "nexus":
            if item.get("runtime_source_commit") != _NEXUS_SOURCE or item.get("build_source_commit") != _NEXUS_SOURCE:
                raise NodeReadinessV2Error("NEXUS source revision drifted")
            if item.get("revision_kind") != "UNCHANGED" or item.get("interface_status") != "SERVICE_INTERFACE_NOT_IMPLEMENTED":
                raise NodeReadinessV2Error("NEXUS revision semantics drifted")
        else:
            if item.get("runtime_source_commit") != _RUNTIME_SOURCE or item.get("build_source_commit") != _BUILD_SOURCE:
                raise NodeReadinessV2Error("SynergyNet source domains drifted")
            if item.get("revision_kind") != "UPDATED" or item.get("interface_status") != "SERVICE_INTERFACE_IMPLEMENTED_SOURCE_ONLY":
                raise NodeReadinessV2Error("SynergyNet revision semantics drifted")
    _expect_digest(revision, "revision_digest", _REVISION_DIGEST)
    return revision


def verify_build_plan_v2(plan: dict[str, Any], revision: dict[str, Any]) -> dict[str, Any]:
    verify_source_revision_v1(revision)
    if plan.get("schema") != "synergy.node-build-plan/v2":
        raise NodeReadinessV2Error("wrong build plan schema")
    if plan.get("profile_digest") != _PROFILE or plan.get("base_source_lock_digest") != _BASE_LOCK:
        raise NodeReadinessV2Error("build plan root binding drifted")
    if plan.get("source_revision_digest") != _REVISION_DIGEST:
        raise NodeReadinessV2Error("build plan source revision drifted")
    services = plan.get("services")
    if not isinstance(services, list) or [item.get("service_id") for item in services] != ["content-cache", "nexus", "synergynet"]:
        raise NodeReadinessV2Error("build plan service set drifted")
    revision_by_id = {item["service_id"]: item for item in revision["services"]}
    for item in services:
        sid = item["service_id"]
        rev = revision_by_id[sid]
        if item.get("runtime_source_commit") != rev["runtime_source_commit"] or item.get("build_source_commit") != rev["build_source_commit"]:
            raise NodeReadinessV2Error("build plan/source revision source mismatch")
        if item.get("service_spec_digest") != _SERVICE_SPEC_DIGESTS[sid]:
            raise NodeReadinessV2Error("build plan ServiceSpec drifted")
        if item.get("build_recipe_digest") != _BUILD_RECIPE_DIGESTS[sid]:
            raise NodeReadinessV2Error("build plan recipe drifted")
        if item.get("build_artifact_digest") is not None or item.get("build_evidence_digest") is not None:
            raise NodeReadinessV2Error("build plan artifact/evidence overclaim")
        if item.get("reproducibility_status") != "NOT_REPRODUCIBLE_TOOLCHAIN_NOT_FROZEN":
            raise NodeReadinessV2Error("build plan reproducibility overclaim")
        if item.get("interface_status") != rev["interface_status"]:
            raise NodeReadinessV2Error("build plan interface status mismatch")
    if plan.get("plan_status") != "BUILD_PLAN_NOT_REPRODUCIBLE_YET":
        raise NodeReadinessV2Error("build plan status drifted")
    if plan.get("build_blockers") != ["BUILD_ARTIFACTS_NOT_VERIFIED", "BUILD_TOOLCHAIN_NOT_FROZEN"]:
        raise NodeReadinessV2Error("build blockers drifted")
    if plan.get("execution_authority") != "NONE":
        raise NodeReadinessV2Error("build plan grants authority")
    _expect_digest(plan, "plan_digest", _PLAN_DIGEST)
    return plan


def verify_readiness_v2(readiness: dict[str, Any], plan: dict[str, Any], revision: dict[str, Any]) -> dict[str, Any]:
    verify_build_plan_v2(plan, revision)
    if readiness.get("schema") != "synergy.node-readiness/v2":
        raise NodeReadinessV2Error("wrong readiness schema")
    if readiness.get("previous_readiness_digest") != _PREVIOUS_READINESS:
        raise NodeReadinessV2Error("readiness ancestry drifted")
    if readiness.get("profile_digest") != _PROFILE or readiness.get("base_source_lock_digest") != _BASE_LOCK:
        raise NodeReadinessV2Error("readiness root binding drifted")
    if readiness.get("source_revision_digest") != _REVISION_DIGEST or readiness.get("build_plan_digest") != _PLAN_DIGEST:
        raise NodeReadinessV2Error("readiness evidence binding drifted")
    current_service_blockers = {
        "NEXUS_SERVICE_INTERFACE_NOT_IMPLEMENTED"
        for item in revision["services"]
        if item["service_id"] == "nexus" and item["interface_status"] == "SERVICE_INTERFACE_NOT_IMPLEMENTED"
    }
    current = {"BUILD_ARTIFACTS_NOT_VERIFIED", "BUILD_TOOLCHAIN_NOT_FROZEN"} | current_service_blockers
    if readiness.get("blockers") != sorted(current):
        raise NodeReadinessV2Error("readiness blockers are not derived from evidence")
    resolved = _V1_BLOCKERS - current
    if readiness.get("resolved_since_v1") != sorted(resolved):
        raise NodeReadinessV2Error("resolved blocker set is not derived from v1 ancestry")
    if readiness.get("build_status") != "BUILD_PLAN_NOT_REPRODUCIBLE_YET":
        raise NodeReadinessV2Error("readiness build status drifted")
    if readiness.get("service_status") != "NEXUS_SERVICE_INTERFACE_INCOMPLETE":
        raise NodeReadinessV2Error("readiness service status drifted")
    if readiness.get("node_status") != "NODE_NOT_DEPLOYABLE" or readiness.get("execution_authority") != "NONE":
        raise NodeReadinessV2Error("readiness cannot grant deployment/execution")
    _expect_digest(readiness, "readiness_digest", _READINESS_DIGEST)
    return readiness


def verify_research_node_readiness_bundle_v2(
    *,
    readiness: dict[str, Any],
    plan: dict[str, Any],
    revision: dict[str, Any],
    nexus_recipe: dict[str, Any],
    synergynet_recipe: dict[str, Any],
    nexus_spec: dict[str, Any],
    content_spec: dict[str, Any],
    relay_spec: dict[str, Any],
) -> dict[str, Any]:
    _verify_service_specs(nexus_spec, content_spec, relay_spec)
    _verify_build_recipes(nexus_recipe, synergynet_recipe)
    verified = verify_readiness_v2(readiness, plan, revision)
    plan_by_id = {item["service_id"]: item for item in plan["services"]}
    if plan_by_id["nexus"]["build_recipe_digest"] != nexus_recipe["recipe_digest"]:
        raise NodeReadinessV2Error("NEXUS recipe bytes are not the plan recipe")
    for sid, spec in (("content-cache", content_spec), ("synergynet", relay_spec)):
        if plan_by_id[sid]["service_spec_digest"] != spec["spec_digest"]:
            raise NodeReadinessV2Error("SynergyNet ServiceSpec bytes are not the plan specs")
        if plan_by_id[sid]["build_recipe_digest"] != synergynet_recipe["recipe_digest"]:
            raise NodeReadinessV2Error("SynergyNet recipe bytes are not the plan recipe")
    if plan_by_id["nexus"]["service_spec_digest"] != nexus_spec["spec_digest"]:
        raise NodeReadinessV2Error("NEXUS ServiceSpec bytes are not the plan spec")
    return verified
