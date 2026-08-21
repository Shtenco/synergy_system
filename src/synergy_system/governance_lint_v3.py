from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any


class GovernanceLintError(ValueError):
    pass


@dataclass(frozen=True)
class Finding:
    repository: str
    path: str
    line: str
    field: str
    value: str
    reason: str


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise GovernanceLintError("JSON root must be object")
    return payload


def validate_schema_registry(registry: dict[str, Any], expected_repositories: set[str]) -> None:
    if registry.get("schema") != "synergy.cross-repo-schema-registry/v1":
        raise GovernanceLintError("unexpected schema registry id")
    policy = registry.get("policy")
    if not isinstance(policy, dict) or not policy or not all(value is True for value in policy.values()):
        raise GovernanceLintError("all schema-registry policies must be enabled")
    if registry.get("authority") != "ARCHITECTURE_REGISTRY_ONLY" or registry.get("execution_authority") != "NONE":
        raise GovernanceLintError("schema registry cannot gain execution authority")
    contracts = registry.get("contracts")
    if not isinstance(contracts, list) or not contracts:
        raise GovernanceLintError("schema contracts required")
    ids: set[str] = set()
    allowed_status = {"CURRENT_DRAFT", "SUPERSEDED_DRAFT", "DOMAIN_CANDIDATE"}
    allowed_visibility = {"FEDERATION", "DOMAIN_INTERNAL"}
    for item in contracts:
        if not isinstance(item, dict) or set(item) != {"id", "producer", "consumers", "status", "visibility"}:
            raise GovernanceLintError("schema contract shape mismatch")
        contract_id = item["id"]
        if not isinstance(contract_id, str) or "/v" not in contract_id or contract_id in ids:
            raise GovernanceLintError("contract ids must be unique versioned strings")
        ids.add(contract_id)
        producer = item["producer"]
        consumers = item["consumers"]
        if producer not in expected_repositories:
            raise GovernanceLintError(f"unknown schema producer: {producer}")
        if not isinstance(consumers, list) or not consumers or consumers != sorted(set(consumers)):
            raise GovernanceLintError("schema consumers must be sorted unique non-empty list")
        if any(consumer not in expected_repositories for consumer in consumers):
            raise GovernanceLintError("schema consumer missing from federation")
        if item["status"] not in allowed_status or item["visibility"] not in allowed_visibility:
            raise GovernanceLintError("unknown schema status/visibility")
        if item["visibility"] == "FEDERATION" and item["status"] == "DOMAIN_CANDIDATE":
            raise GovernanceLintError("domain candidate cannot be advertised as federation contract")


def validate_authority_policy(policy: dict[str, Any], expected_repositories: set[str]) -> None:
    if policy.get("schema") != "synergy.authority-lint-policy/v1":
        raise GovernanceLintError("unexpected authority-lint policy schema")
    prefixes = policy.get("scan_path_prefixes")
    if not isinstance(prefixes, list) or not prefixes or prefixes != sorted(set(prefixes)):
        raise GovernanceLintError("scan path prefixes must be sorted unique")
    fields = policy.get("fields")
    if not isinstance(fields, dict) or not fields:
        raise GovernanceLintError("authority fields required")
    for field, rule in fields.items():
        if not isinstance(field, str) or not field.endswith("authority"):
            raise GovernanceLintError("authority policy field names must end in authority")
        if not isinstance(rule, dict) or set(rule) != {"non_none_allowed_repositories"}:
            raise GovernanceLintError("authority rule shape mismatch")
        repos = rule["non_none_allowed_repositories"]
        if not isinstance(repos, list) or repos != sorted(set(repos)):
            raise GovernanceLintError("allowed repositories must be sorted unique")
        if any(repo not in expected_repositories for repo in repos):
            raise GovernanceLintError("authority policy references unknown repository")
    none_values = policy.get("none_values")
    if not isinstance(none_values, list) or not none_values or none_values != sorted(set(none_values)):
        raise GovernanceLintError("none_values must be sorted unique")


def _extract_claim(line: str, field: str) -> str | None:
    # Handles common JSON/YAML/Python forms such as:
    # "execution_authority": "NONE"
    # execution_authority: NONE
    # execution_authority: str = "NONE"
    patterns = [
        rf'["\']?{re.escape(field)}["\']?\s*:\s*["\']?([A-Z][A-Z0-9_]*)["\']?',
        rf'\b{re.escape(field)}\b\s*:\s*[A-Za-z_][A-Za-z0-9_\[\], ]*\s*=\s*["\']?([A-Z][A-Z0-9_]*)["\']?',
        rf'\b{re.escape(field)}\b\s*=\s*["\']?([A-Z][A-Z0-9_]*)["\']?',
    ]
    for pattern in patterns:
        match = re.search(pattern, line)
        if match:
            return match.group(1)
    return None


def lint_patch(*, repository: str, path: str, patch: str, policy: dict[str, Any], expected_repositories: set[str]) -> tuple[Finding, ...]:
    if repository not in expected_repositories:
        raise GovernanceLintError("repository is outside frozen federation")
    validate_authority_policy(policy, expected_repositories)
    if not isinstance(path, str) or not isinstance(patch, str):
        raise GovernanceLintError("path and patch must be strings")
    prefixes = tuple(policy["scan_path_prefixes"])
    if not path.startswith(prefixes):
        return ()
    none_values = set(policy["none_values"])
    findings: list[Finding] = []
    for raw in patch.splitlines():
        if not raw.startswith("+") or raw.startswith("+++"):
            continue
        line = raw[1:]
        for field, rule in policy["fields"].items():
            value = _extract_claim(line, field)
            if value is None or value in none_values:
                continue
            allowed = set(rule["non_none_allowed_repositories"])
            if repository not in allowed:
                findings.append(Finding(repository, path, line, field, value, "NON_NONE_AUTHORITY_OUTSIDE_ALLOWED_OWNER_SET"))
    return tuple(findings)


def assert_patch_allowed(**kwargs: Any) -> None:
    findings = lint_patch(**kwargs)
    if findings:
        summary = "; ".join(f"{f.path}:{f.field}={f.value}" for f in findings)
        raise GovernanceLintError(f"forbidden authority transition: {summary}")
