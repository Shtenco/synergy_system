from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


class FederationError(ValueError):
    pass


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader: yaml.Loader, node: yaml.Node, deep: bool = False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise FederationError(f"duplicate YAML key: {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


_FORBIDDEN_FACT_EDGES = {
    ("Shtenco/agi_nexus", "Shtenco/synergy_pay_system"),
    ("Shtenco/nexus_science_agent", "Shtenco/synergy_pay_system"),
    ("Shtenco/synergynet", "Shtenco/synergy_financial_os"),
    ("Shtenco/synergychain.github.io", "Shtenco/synergy_pay_system"),
    ("Shtenco/shtenco.github.io", "Shtenco/synergy_pay_system"),
    ("Shtenco/shtencoauantai.github.io", "Shtenco/synergy_pay_system"),
}
_ALLOWED_MUTUAL_PAIR = frozenset({"Shtenco/synergy_financial_os", "Shtenco/synergy_pay_system"})
_NON_AUTHORITY_CLASSES = {"PRESENTATION", "PUBLIC_PROVENANCE", "APPLICATION_CLIENT", "APPLICATION_CONTROL_PLANE"}


def load_federation(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = yaml.load(handle, Loader=_UniqueKeyLoader)
    if not isinstance(payload, dict):
        raise FederationError("federation root must be a mapping")
    return payload


def load_expected_repositories(path: str | Path) -> set[str]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("schema") != "synergy.expected-repositories/v1":
        raise FederationError("unexpected expected-repository schema")
    repos = payload.get("repositories")
    if not isinstance(repos, list) or not repos:
        raise FederationError("expected repository list must be non-empty")
    if repos != sorted(repos) or len(repos) != len(set(repos)):
        raise FederationError("expected repository list must be sorted and unique")
    return set(repos)


def _authority_fields(entry: dict[str, Any]) -> list[tuple[str, Any]]:
    result = []
    for key, value in entry.items():
        if key == "authority" or key.endswith("_authority"):
            result.append((key, value))
    return result


def validate_federation(payload: dict[str, Any], expected_repositories: set[str]) -> None:
    if payload.get("schema") != "synergy.repository-federation/v1":
        raise FederationError("unexpected federation schema")
    if payload.get("architecture_root") != "Shtenco/synergy_system":
        raise FederationError("architecture root drifted")

    policy = payload.get("policy")
    if not isinstance(policy, dict) or not policy or not all(value is True for value in policy.values()):
        raise FederationError("all v1 federation policies must be explicitly enabled")
    required_policy = {
        "federation_not_monorepo",
        "preserve_legacy_generations",
        "one_authority_per_fact",
        "no_new_repo_without_unique_responsibility",
        "presentation_is_not_authority",
        "ai_is_not_execution_authority",
        "blockchain_is_not_accounting_authority",
    }
    if set(policy) != required_policy:
        raise FederationError("federation policy set drifted")

    repositories = payload.get("repositories")
    if not isinstance(repositories, list) or not repositories:
        raise FederationError("repositories must be a non-empty list")
    by_repo: dict[str, dict[str, Any]] = {}
    for entry in repositories:
        if not isinstance(entry, dict):
            raise FederationError("repository entry must be an object")
        repo = entry.get("repo")
        if not isinstance(repo, str) or not repo.startswith("Shtenco/") or repo in by_repo:
            raise FederationError("repository ids must be unique explicit Shtenco/* names")
        if not isinstance(entry.get("class"), str) or not entry["class"]:
            raise FederationError(f"repository class missing: {repo}")
        if not isinstance(entry.get("role"), str) or not entry["role"]:
            raise FederationError(f"repository role missing: {repo}")
        by_repo[repo] = entry

    actual_repositories = set(by_repo)
    if actual_repositories != expected_repositories:
        missing = sorted(expected_repositories - actual_repositories)
        extra = sorted(actual_repositories - expected_repositories)
        raise FederationError(f"repository set mismatch; missing={missing}, extra={extra}")

    root_entry = by_repo["Shtenco/synergy_system"]
    if root_entry.get("execution_authority") != "NONE":
        raise FederationError("architecture root must not gain execution authority")

    authorities = payload.get("exclusive_authorities")
    if not isinstance(authorities, dict) or not authorities:
        raise FederationError("exclusive authorities are required")
    for authority, owner in authorities.items():
        if not isinstance(authority, str) or not authority:
            raise FederationError("authority key must be non-empty")
        if owner not in by_repo:
            raise FederationError(f"authority owner is missing from repository map: {authority}")
        if by_repo[owner]["class"] in _NON_AUTHORITY_CLASSES:
            raise FederationError(f"non-authority class owns exclusive authority: {owner}")

    for repo, entry in by_repo.items():
        if entry["class"] in _NON_AUTHORITY_CLASSES:
            for field, value in _authority_fields(entry):
                if value != "NONE":
                    raise FederationError(f"{repo} has forbidden {field}={value!r}")

    edges = payload.get("canonical_dependency_direction")
    if not isinstance(edges, list):
        raise FederationError("canonical_dependency_direction must be a list")
    seen_edges: set[tuple[str, str, str]] = set()
    directed_pairs: set[tuple[str, str]] = set()
    for edge in edges:
        if not isinstance(edge, dict) or set(edge) != {"from", "to", "contract"}:
            raise FederationError("dependency edge must have from/to/contract only")
        source, target, contract = edge["from"], edge["to"], edge["contract"]
        if source not in by_repo or target not in by_repo:
            raise FederationError("dependency endpoint missing from repository map")
        if source == target:
            raise FederationError("self-dependency is forbidden")
        if not isinstance(contract, str) or not contract:
            raise FederationError("dependency contract is required")
        identity = (source, target, contract)
        if identity in seen_edges:
            raise FederationError("duplicate dependency edge")
        seen_edges.add(identity)
        if (source, target) in _FORBIDDEN_FACT_EDGES:
            raise FederationError(f"forbidden direct fact-authority edge: {source} -> {target}")
        directed_pairs.add((source, target))

    for source, target in directed_pairs:
        if (target, source) in directed_pairs and frozenset({source, target}) != _ALLOWED_MUTUAL_PAIR:
            raise FederationError(f"unexpected bidirectional authority/data cycle: {source} <-> {target}")

    statuses = payload.get("status_vocabulary")
    if not isinstance(statuses, list) or statuses != list(dict.fromkeys(statuses)) or not statuses:
        raise FederationError("status vocabulary must be unique and non-empty")
    verification = payload.get("verification_vocabulary")
    if not isinstance(verification, list) or verification != list(dict.fromkeys(verification)) or not verification:
        raise FederationError("verification vocabulary must be unique and non-empty")
