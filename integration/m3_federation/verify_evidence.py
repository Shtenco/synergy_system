#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence" / "m3_federation_result.json"
LOCK = HERE / "integration_lock_v1.json"
INTERFACES = HERE.parents[1] / "registry" / "REPOSITORY_INTERFACES.json"

EXPECTED_VERTICALS = {
    "trading",
    "science",
    "engineering",
    "real-economy",
    "runtime-network",
    "trust-ui",
}


def expected_runtime_edges() -> set[tuple[str, str, str]]:
    data = json.loads(INTERFACES.read_text(encoding="utf-8"))
    edges: set[tuple[str, str, str]] = set()
    for repository in data["repositories"]:
        for edge in repository.get("runtime_out", []):
            if edge.get("status") == "ADAPTER_IMPLEMENTED":
                edges.add((repository["repo"], edge["to"], edge["contract_id"]))
    return edges


def main() -> int:
    if not EVIDENCE.is_file():
        print("ERROR: evidence file missing")
        return 1

    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    if data.get("schema") != "synergy.m3-federation-evidence/v2":
        print("ERROR: schema mismatch")
        return 1

    lock_hash = hashlib.sha256(LOCK.read_bytes()).hexdigest()
    if data.get("lock_sha256") != lock_hash:
        print("ERROR: lock hash mismatch")
        return 1
    if data.get("lock_repository_count") != 20:
        print("ERROR: lock repository count mismatch")
        return 1

    results = data.get("results")
    if not isinstance(results, list):
        print("ERROR: results missing")
        return 1
    if {x.get("name") for x in results} != EXPECTED_VERTICALS:
        print("ERROR: vertical set mismatch")
        return 1
    if len(results) != len(EXPECTED_VERTICALS):
        print("ERROR: duplicate/missing vertical result")
        return 1
    if any(x.get("status") != "PASS" for x in results):
        print("ERROR: one or more verticals failed")
        return 1

    witnesses = data.get("edge_witnesses")
    if not isinstance(witnesses, list):
        print("ERROR: edge witnesses missing")
        return 1
    actual = {
        (x.get("from"), x.get("to"), x.get("contract_id"))
        for x in witnesses
    }
    expected = expected_runtime_edges()
    if len(witnesses) != 22 or len(actual) != 22:
        print(f"ERROR: witness cardinality mismatch witnesses={len(witnesses)} unique={len(actual)}")
        return 1
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        print("ERROR: edge witness set does not match registry")
        print("missing", missing)
        print("extra", extra)
        return 1
    if data.get("edge_witness_count") != 22 or data.get("expected_edge_count") != 22:
        print("ERROR: edge count fields mismatch")
        return 1
    if data.get("all_pass") is not True:
        print("ERROR: M3 evidence is not all-pass")
        return 1

    print("M3 FEDERATION EVIDENCE V2: VERIFIED")
    print("lock_sha256", lock_hash)
    print("runtime_edges", len(expected))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
