#!/usr/bin/env python3
"""Validate internal consistency of the SYNERGY 75-repository federation registry."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "SYNERGY_REPOSITORIES.json"

REQUIRED_TOP = {
    "repository_count",
    "architecture_root",
    "master_dossier",
    "civilization_graph",
    "runtime_orchestrator",
    "repositories",
}

def fail(msg: str) -> None:
    print(f"ERROR: {msg}")
    raise SystemExit(1)

def main() -> int:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    missing = REQUIRED_TOP - data.keys()
    if missing:
        fail(f"registry missing top-level keys: {sorted(missing)}")

    repos = data["repositories"]
    if data["repository_count"] != len(repos):
        fail(
            f"repository_count={data['repository_count']} but "
            f"repositories has {len(repos)} entries"
        )

    if len(repos) != 75:
        fail(f"canonical federation must contain 75 repositories, got {len(repos)}")

    full_names = [r["full_name"] for r in repos]
    names = [r["name"] for r in repos]

    if len(full_names) != len(set(full_names)):
        fail("duplicate full_name entries")
    if len(names) != len(set(names)):
        fail("duplicate repository names")

    by_name = {r["name"]: r for r in repos}

    for r in repos:
        if not r["full_name"].startswith("Shtenco/"):
            fail(f"unexpected owner in {r['full_name']}")
        parent = r.get("federation_parent")
        if parent and parent not in by_name:
            fail(f"{r['name']} has missing federation_parent={parent}")
        if r.get("classification_basis") != (
            "architectural documentation classification; "
            "not proof of runtime dependency"
        ):
            fail(f"{r['name']} lost architecture/runtime distinction")

    expected = {
        "Shtenco/synergy_system",
        "Shtenco/synergy_project",
        "Shtenco/synergy_megaproject",
        "Shtenco/synergy_meta_os",
    }
    for key in (
        "architecture_root",
        "master_dossier",
        "civilization_graph",
        "runtime_orchestrator",
    ):
        if data[key] not in expected:
            fail(f"unexpected master reference {key}={data[key]}")
        if data[key] not in full_names:
            fail(f"master reference not present in repositories: {data[key]}")

    print(f"OK: {len(repos)} unique repositories")
    print("OK: all federation parents resolve")
    print("OK: master references resolve")
    print("OK: architecture/runtime distinction preserved")
    return 0

if __name__ == "__main__":
    sys.exit(main())
