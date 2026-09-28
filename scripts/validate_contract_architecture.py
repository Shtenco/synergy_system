#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REPOS = ROOT / "registry" / "SYNERGY_REPOSITORIES.json"
AUTH = ROOT / "registry" / "AUTHORITY_REGISTRY.json"
CONTRACTS = ROOT / "registry" / "CONTRACT_REGISTRY.json"
GRAPH = ROOT / "registry" / "DEPENDENCY_GRAPH.json"
SCHEMAS = ROOT / "contracts" / "schemas"

def fail(msg: str) -> None:
    print(f"ERROR: {msg}")
    raise SystemExit(1)

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    repos = load(REPOS)
    auth = load(AUTH)
    contracts = load(CONTRACTS)
    graph = load(GRAPH)

    repo_names = {r["full_name"] for r in repos["repositories"]}
    authority_names = set(auth["authorities"])
    contract_ids = set()

    for name, spec in auth["authorities"].items():
        if spec["owner"] not in repo_names:
            fail(f"authority {name} owner missing: {spec['owner']}")

    for c in contracts["contracts"]:
        cid = c["contract_id"]
        if cid in contract_ids:
            fail(f"duplicate contract_id {cid}")
        contract_ids.add(cid)
        if c["producer"] not in repo_names:
            fail(f"{cid}: producer missing")
        for consumer in c["consumers"]:
            if consumer not in repo_names:
                fail(f"{cid}: consumer missing {consumer}")
        if c["authority"] not in authority_names:
            fail(f"{cid}: unknown authority {c['authority']}")
        path = ROOT / c["schema_path"]
        if not path.is_file():
            fail(f"{cid}: schema missing {path}")
        schema = load(path)
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            fail(f"{cid}: schema draft mismatch")

    graph_contracts = {
        e["contract_id"]
        for e in graph["edges"]
        if e["type"] == "CONTRACT_FLOW"
    }
    missing = contract_ids - graph_contracts
    if missing:
        fail(f"contracts absent from dependency graph: {sorted(missing)}")

    runtime_edges = [e for e in graph["edges"] if e["type"] == "RUNTIME_DEPENDENCY"]
    for e in runtime_edges:
        if not e.get("evidence"):
            fail(f"runtime edge lacks evidence: {e}")

    envelope = load(SCHEMAS / "event-envelope-v1.schema.json")
    pattern = envelope["properties"]["contract_id"]["pattern"]
    rx = re.compile(pattern)
    for cid in contract_ids:
        if not rx.match(cid):
            fail(f"contract id violates envelope pattern: {cid}")

    print(f"OK: {len(repo_names)} repositories")
    print(f"OK: {len(authority_names)} authorities")
    print(f"OK: {len(contract_ids)} typed contracts")
    print(f"OK: {len(graph['edges'])} dependency edges")
    print("OK: all producers/consumers/authorities/schemas resolve")
    return 0

if __name__ == "__main__":
    sys.exit(main())
