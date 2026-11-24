#!/usr/bin/env python3
"""Validate the 92-record federation-reviewed owner inventory and its 75-record interface scope.

The owner inventory is not the same thing as the runtime/interface maturity registry.
Legacy names are retained as explicitly unverified rename candidates until immutable
GitHub identity or Git ancestry evidence confirms the lineage.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "registry"
REGISTRY = REG / "SYNERGY_REPOSITORIES.json"
INTERFACES = REG / "REPOSITORY_INTERFACES.json"
RENAMES = REG / "REPOSITORY_RENAME_CANDIDATES.json"

REQUIRED_TOP = {
    "repository_count", "architecture_root", "master_dossier",
    "civilization_graph", "runtime_orchestrator", "repositories",
}
ALLOWED_CLASSIFICATION_BASES = {
    "architectural documentation classification; not proof of runtime dependency",
    "renamed repository lineage; revalidate README passport, active branches and runtime dependency before marking complete",
    "provisional inventory classification from current README/main tree and selected branch evidence; federation_parent is not proof of runtime dependency",
    "targeted source/branch/CI review on 2026-11-20; branch evidence does not imply merged main runtime or deployment",
    "targeted source/branch/CI review on 2026-11-20; branch evidence does not imply merged main runtime or deployment",
}
ALLOWED_DEEP_PASS = {"COMPLETE", "PENDING_RENAME_REVALIDATION", "PENDING"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def main() -> int:
    data = load(REGISTRY)
    missing = REQUIRED_TOP - data.keys()
    if missing:
        fail(f"registry missing top-level keys: {sorted(missing)}")

    repos = data["repositories"]
    if not isinstance(repos, list) or data["repository_count"] != len(repos):
        fail(
            f"repository_count={data.get('repository_count')} but "
            f"repositories has {len(repos) if isinstance(repos, list) else 'non-list'} entries"
        )

    if len(repos) != 92:
        fail(f"expected 92 federation-reviewed owner repositories, got {len(repos)}")

    full_names = [r.get("full_name") for r in repos]
    names = [r.get("name") for r in repos]
    if None in full_names or None in names:
        fail("every inventory row must have name and full_name")
    if len(full_names) != len(set(full_names)):
        fail("duplicate full_name entries")
    if len(names) != len(set(names)):
        fail("duplicate repository names")

    by_name = {r["name"]: r for r in repos}
    full_name_set = set(full_names)
    for r in repos:
        if not r["full_name"].startswith("Shtenco/"):
            fail(f"unexpected owner in {r['full_name']}")
        parent = r.get("federation_parent")
        if parent and parent not in by_name:
            fail(f"{r['name']} has missing federation_parent={parent}")
        if r.get("classification_basis") not in ALLOWED_CLASSIFICATION_BASES:
            fail(f"{r['name']} has an unknown classification_basis")
        if r.get("readme_deep_pass") not in ALLOWED_DEEP_PASS:
            fail(f"{r['name']} has an unknown readme_deep_pass status")
        if r["readme_deep_pass"] == "PENDING_RENAME_REVALIDATION" and not r.get("classification_basis", "").startswith("renamed repository lineage"):
            fail(f"{r['name']} is pending rename review without rename-lineage classification")
        if r["readme_deep_pass"] == "PENDING" and not r.get("classification_basis", "").startswith("provisional inventory classification"):
            fail(f"{r['name']} is pending initial review without provisional classification")

    expected = {
        "Shtenco/synergy_system",
        "Shtenco/synergy_project",
        "Shtenco/synergy_megaproject",
        "Shtenco/synergy_meta_os",
    }
    for key in (
        "architecture_root", "master_dossier", "civilization_graph",
        "runtime_orchestrator",
    ):
        if data[key] not in expected:
            fail(f"unexpected master reference {key}={data[key]}")
        if data[key] not in full_name_set:
            fail(f"master reference not present in inventory: {data[key]}")

    interfaces = load(INTERFACES)
    interface_repos = interfaces.get("repositories", [])
    interface_names = [r.get("repo") for r in interface_repos]
    if interfaces.get("repository_count") != len(interface_repos) or len(interface_repos) != 77:
        fail("interface registry must retain its separate 77-record scope")
    if len(interface_names) != len(set(interface_names)):
        fail("duplicate repository names in interface registry")

    rename_data = load(RENAMES)
    if rename_data.get("schema") != "synergy.repository-rename-candidates.v1":
        fail("unsupported repository rename candidate schema")
    candidates = rename_data.get("candidates", [])
    legacy_names = [x.get("legacy_full_name") for x in candidates]
    if len(legacy_names) != len(set(legacy_names)):
        fail("duplicate legacy names in rename candidates")
    if len(candidates) != 3:
        fail(f"expected 3 explicitly unverified historical rename candidates, got {len(candidates)}")
    for item in candidates:
        if item.get("status") != "CANDIDATE_ONLY" or item.get("identity_confirmed") is not False:
            fail("rename candidate must remain explicitly unconfirmed")
        if item.get("legacy_full_name") in full_name_set:
            fail(f"legacy name unexpectedly remains in current inventory: {item.get('legacy_full_name')}")
        if item.get("candidate_full_name") not in full_name_set:
            fail(f"rename candidate target missing from inventory: {item.get('candidate_full_name')}")

    unmatched_interfaces = set(interface_names) - full_name_set
    if unmatched_interfaces != set(legacy_names):
        fail(
            "interface/inventory name mismatch differs from explicit unverified rename candidates: "
            f"unmatched={sorted(unmatched_interfaces)} candidates={sorted(legacy_names)}"
        )

    print(f"OK: {len(repos)} unique current owner-inventory entries")
    print(f"OK: {len(interface_repos)} unique interface-scope entries")
    print(f"OK: {len(candidates)} legacy names remain explicitly unverified")
    print("OK: all federation parents resolve")
    print("OK: master references resolve")
    print("OK: provisional, renamed and completed documentation states remain distinct")
    return 0


if __name__ == "__main__":
    sys.exit(main())
