#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def generate():
    rr = load("registry/SYNERGY_REPOSITORIES.json")
    ar = load("registry/AUTHORITY_REGISTRY.json")
    cr = load("registry/CONTRACT_REGISTRY.json")
    dg = load("registry/DEPENDENCY_GRAPH.json")
    current = load("registry/REPOSITORY_INTERFACES.json")

    # The interface registry is an intentional federation subset of the owner inventory.
    # Keep its scope explicit: adding an owner repository does not silently add it as a
    # runtime/interface component. A new component must first be reviewed and registered.
    scope = {row["repo"] for row in current["repositories"]}
    current_by_repo = {row["repo"]: row for row in current["repositories"]}

    owned = {}
    for name, spec in ar["authorities"].items():
        owned.setdefault(spec["owner"], []).append(name)

    produces = {}
    consumes = {}
    for contract in cr["contracts"]:
        produces.setdefault(contract["producer"], []).append({
            "contract_id": contract["contract_id"],
            "status": contract.get("producer_status", "DEFINED"),
            "authority": contract["authority"],
        })
        for repo in contract["consumers"]:
            consumes.setdefault(repo, []).append({
                "contract_id": contract["contract_id"],
                "status": contract.get("consumer_status", {}).get(repo, "DEFINED"),
                "authority": contract["authority"],
            })

    runtime_in = {}
    runtime_out = {}
    for edge in dg["edges"]:
        if edge["type"] != "RUNTIME_DEPENDENCY":
            continue
        runtime_out.setdefault(edge["from"], []).append({
            "to": edge["to"],
            "contract_id": edge.get("contract_id"),
            "status": edge["status"],
            "evidence": edge.get("evidence", []),
        })
        runtime_in.setdefault(edge["to"], []).append({
            "from": edge["from"],
            "contract_id": edge.get("contract_id"),
            "status": edge["status"],
            "evidence": edge.get("evidence", []),
        })

    interfaces = []
    for repo in rr["repositories"]:
        full_name = repo["full_name"]
        if full_name not in scope:
            continue

        produced = sorted(produces.get(full_name, []), key=lambda x: x["contract_id"])
        consumed = sorted(consumes.get(full_name, []), key=lambda x: x["contract_id"])
        out_edges = runtime_out.get(full_name, [])
        in_edges = runtime_in.get(full_name, [])

        if out_edges or in_edges:
            status = "ADAPTER_INTEGRATED"
        elif any(x["status"] == "IMPLEMENTED" for x in [*produced, *consumed]):
            status = "PARTIAL_IMPLEMENTATION"
        elif produced or consumed:
            status = "CONTRACT_DEFINED"
        else:
            # Preserve reviewed non-runtime / pending classifications for scoped components.
            status = current_by_repo[full_name].get("interface_status", "ARCHITECTURAL_ONLY")

        interfaces.append({
            "repo": full_name,
            "domain": repo["domain"],
            "role": repo["role"],
            "federation_parent": f"Shtenco/{repo['federation_parent']}" if repo.get("federation_parent") else None,
            "authorities_owned": sorted(owned.get(full_name, [])),
            "produces": produced,
            "consumes": consumed,
            "runtime_out": out_edges,
            "runtime_in": in_edges,
            "interface_status": status,
        })

    return {
        "schema": current.get("schema", "synergy.repository-interfaces/v1"),
        "as_of": current.get("as_of", "2026-11-20"),
        "repository_count": len(interfaces),
        "semantics": current.get("semantics", {}),
        "repositories": interfaces,
    }


if __name__ == "__main__":
    print(json.dumps(generate(), ensure_ascii=False, indent=2))
