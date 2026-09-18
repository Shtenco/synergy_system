#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

CATALOG_SCHEMA = "synergy.repository-catalog/v5"
LIFECYCLE = {"CANONICAL", "CANDIDATE", "R&D", "LEGACY", "ARCHIVE"}
AUTHORITY_KEYS = {
    "execution", "financial", "accounting", "payment", "settlement",
    "blockchain_submission", "code_write", "external_side_effect",
}
ECONOMIC_AUTHORITIES = {"financial", "accounting", "payment", "settlement"}
EXCLUSIVE_AUTHORITIES = {
    "financial", "accounting", "payment", "settlement", "blockchain_submission",
}
MANDATORY_REPOSITORY_FIELDS = {
    "name", "github_id", "repo_url", "default_branch", "visibility",
    "lifecycle_status", "system_kind", "domain", "role", "risk_class",
    "federation_membership", "trust_enabled", "authority",
    "capabilities_provided", "capabilities_consumed",
    "allowed_exchange_objects", "canonical_successor",
    "provenance_sources", "verification",
}


def canonical_catalog_bytes(catalog: dict[str, Any]) -> bytes:
    return json.dumps(
        catalog,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def catalog_digest(catalog: dict[str, Any]) -> str:
    return hashlib.sha3_256(canonical_catalog_bytes(catalog)).hexdigest()


def load_catalog(path: str | Path = "config/repository_catalog_v5.json") -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _duplicates(values: list[str]) -> set[str]:
    seen: set[str] = set()
    dup: set[str] = set()
    for value in values:
        if value in seen:
            dup.add(value)
        seen.add(value)
    return dup


def _successor_cycle(repositories: list[dict[str, Any]]) -> list[str] | None:
    successors = {
        str(r["name"]): str(r["canonical_successor"])
        for r in repositories
        if r.get("canonical_successor")
    }
    known = {str(r["name"]) for r in repositories}
    for name, successor in successors.items():
        if successor not in known:
            return [name, successor]

    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        mark = state.get(node, 0)
        if mark == 1:
            if node in stack:
                i = stack.index(node)
                return stack[i:] + [node]
            return [node, node]
        if mark == 2:
            return None
        state[node] = 1
        stack.append(node)
        nxt = successors.get(node)
        if nxt:
            cycle = visit(nxt)
            if cycle:
                return cycle
        stack.pop()
        state[node] = 2
        return None

    for node in sorted(successors):
        cycle = visit(node)
        if cycle:
            return cycle
    return None


def validate_catalog(catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if catalog.get("schema") != CATALOG_SCHEMA:
        errors.append(f"E_SCHEMA:{catalog.get('schema')!r}")
    if "repository_count" in catalog:
        errors.append("E_HARDCODED_REPOSITORY_COUNT:repository_count")

    repositories = catalog.get("repositories")
    if not isinstance(repositories, list) or not repositories:
        return errors + ["E_REPOSITORIES:missing_or_empty"]

    names = [str(r.get("name", "")) for r in repositories if isinstance(r, dict)]
    ids = [str(r.get("github_id", "")) for r in repositories if isinstance(r, dict)]
    urls = [str(r.get("repo_url", "")) for r in repositories if isinstance(r, dict)]

    for value in sorted(_duplicates(names)):
        errors.append(f"E_DUPLICATE_NAME:{value}")
    for value in sorted(_duplicates(ids)):
        errors.append(f"E_DUPLICATE_GITHUB_ID:{value}")
    for value in sorted(_duplicates(urls)):
        errors.append(f"E_DUPLICATE_REPO_URL:{value}")

    canonical_owners: dict[str, list[str]] = {k: [] for k in EXCLUSIVE_AUTHORITIES}

    for index, repo in enumerate(repositories):
        if not isinstance(repo, dict):
            errors.append(f"E_REPOSITORY_TYPE:{index}")
            continue

        name = str(repo.get("name") or f"index:{index}")
        missing = sorted(MANDATORY_REPOSITORY_FIELDS - set(repo))
        if missing:
            errors.append(f"E_MISSING_FIELDS:{name}:{','.join(missing)}")
            continue

        lifecycle = repo.get("lifecycle_status")
        if lifecycle not in LIFECYCLE:
            errors.append(f"E_LIFECYCLE:{name}:{lifecycle}")

        authority = repo.get("authority")
        if not isinstance(authority, dict) or set(authority) != AUTHORITY_KEYS:
            errors.append(f"E_AUTHORITY_SHAPE:{name}")
            continue

        if lifecycle == "ARCHIVE":
            if bool(repo.get("trust_enabled")) or bool(repo.get("federation_membership")):
                errors.append(f"E_ARCHIVE_TRUST:{name}")

        if lifecycle == "LEGACY" and bool(repo.get("trust_enabled")):
            errors.append(f"E_LEGACY_TRUST:{name}")

        if lifecycle == "R&D":
            for key in sorted(ECONOMIC_AUTHORITIES):
                if authority.get(key) != "NONE":
                    errors.append(f"E_RND_ECONOMIC_AUTHORITY:{name}:{key}")

        if repo.get("system_kind") == "PRESENTATION":
            for key in sorted(ECONOMIC_AUTHORITIES | {"execution", "blockchain_submission"}):
                if authority.get(key) != "NONE":
                    errors.append(f"E_PRESENTATION_ECONOMIC_AUTHORITY:{name}:{key}")

        if lifecycle == "CANONICAL":
            for key in EXCLUSIVE_AUTHORITIES:
                if authority.get(key) == "CANONICAL":
                    canonical_owners[key].append(name)

    for key, owners in sorted(canonical_owners.items()):
        if len(owners) > 1:
            errors.append(f"E_AUTHORITY_AMBIGUOUS:{key}:{','.join(sorted(owners))}")

    cycle = _successor_cycle(repositories)
    if cycle:
        errors.append(f"E_SUCCESSOR_CYCLE:{'->'.join(cycle)}")

    return errors


def assert_valid_catalog(catalog: dict[str, Any]) -> None:
    errors = validate_catalog(catalog)
    if errors:
        raise ValueError("\n".join(errors))


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate SYNERGY Federation V5 catalog")
    parser.add_argument(
        "catalog",
        nargs="?",
        default="config/repository_catalog_v5.json",
        help="catalog path",
    )
    args = parser.parse_args()
    catalog = load_catalog(args.catalog)
    errors = validate_catalog(catalog)
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({
        "ok": True,
        "repositories": len(catalog["repositories"]),
        "catalog_digest": catalog_digest(catalog),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
