#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

def generate():
    rr=load("registry/SYNERGY_REPOSITORIES.json")
    ar=load("registry/AUTHORITY_REGISTRY.json")
    cr=load("registry/CONTRACT_REGISTRY.json")
    dg=load("registry/DEPENDENCY_GRAPH.json")

    owned={}
    for name,spec in ar["authorities"].items():
        owned.setdefault(spec["owner"],[]).append(name)
    produces={};consumes={}
    for c in cr["contracts"]:
        produces.setdefault(c["producer"],[]).append({
            "contract_id":c["contract_id"],
            "status":c.get("producer_status","DEFINED"),
            "authority":c["authority"],
        })
        for repo in c["consumers"]:
            consumes.setdefault(repo,[]).append({
                "contract_id":c["contract_id"],
                "status":c.get("consumer_status",{}).get(repo,"DEFINED"),
                "authority":c["authority"],
            })
    rin={};rout={}
    for e in dg["edges"]:
        if e["type"]!="RUNTIME_DEPENDENCY": continue
        rout.setdefault(e["from"],[]).append({
            "to":e["to"],"contract_id":e.get("contract_id"),
            "status":e["status"],"evidence":e.get("evidence",[])
        })
        rin.setdefault(e["to"],[]).append({
            "from":e["from"],"contract_id":e.get("contract_id"),
            "status":e["status"],"evidence":e.get("evidence",[])
        })
    interfaces=[]
    for r in rr["repositories"]:
        p=produces.get(r["full_name"],[])
        c=consumes.get(r["full_name"],[])
        ro=rout.get(r["full_name"],[])
        ri=rin.get(r["full_name"],[])
        status="ARCHITECTURAL_ONLY"
        if p or c: status="CONTRACT_DEFINED"
        if any(x["status"]=="IMPLEMENTED" for x in [*p,*c]): status="PARTIAL_IMPLEMENTATION"
        if ro or ri: status="ADAPTER_INTEGRATED"
        interfaces.append({
            "repo":r["full_name"],"domain":r["domain"],"role":r["role"],
            "federation_parent":f"Shtenco/{r['federation_parent']}" if r.get("federation_parent") else None,
            "authorities_owned":sorted(owned.get(r["full_name"],[])),
            "produces":sorted(p,key=lambda x:x["contract_id"]),
            "consumes":sorted(c,key=lambda x:x["contract_id"]),
            "runtime_out":ro,"runtime_in":ri,"interface_status":status,
        })
    return {
        "schema":"synergy.repository-interfaces/v1",
        "as_of":"2026-09-28",
        "repository_count":len(interfaces),
        "semantics":{
            "ARCHITECTURAL_ONLY":"No typed producer/consumer interface is defined yet.",
            "CONTRACT_DEFINED":"At least one typed contract is defined but no endpoint adapter is proven.",
            "PARTIAL_IMPLEMENTATION":"At least one producer or consumer implementation exists.",
            "ADAPTER_INTEGRATED":"At least one runtime dependency has executable adapters on both endpoints.",
        },
        "repositories":interfaces,
    }

if __name__=="__main__":
    print(json.dumps(generate(),ensure_ascii=False,indent=2))
