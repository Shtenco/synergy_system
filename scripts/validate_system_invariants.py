#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(name):
    return json.loads((ROOT/name).read_text(encoding="utf-8"))

def main():
    auth=load("registry/AUTHORITY_REGISTRY.json")
    contracts=load("registry/CONTRACT_REGISTRY.json")
    graph=load("registry/DEPENDENCY_GRAPH.json")
    inv=load("registry/INVARIANT_REGISTRY.json")

    owner_to_authority={}
    for name,spec in auth["authorities"].items():
        owner_to_authority.setdefault(spec["owner"],set()).add(name)

    runtime=[e for e in graph["edges"] if e["type"]=="RUNTIME_DEPENDENCY"]
    errors=[]

    for edge in runtime:
        if not edge.get("evidence"):
            errors.append(f"runtime edge without evidence: {edge}")
        if edge["from"]=="Shtenco/synergy_trademux" and edge["to"]=="Shtenco/synergy_financial_os":
            errors.append("TradeMux must not bypass Pay settlement/reconciliation")
        fa=owner_to_authority.get(edge["from"],set())
        ta=owner_to_authority.get(edge["to"],set())
        if "blockchain_trust" in fa and "canonical_accounting" in ta:
            errors.append("blockchain trust must not author accounting")
        if "runtime_orchestration" in fa and "canonical_accounting" in ta:
            errors.append("runtime root must not author accounting")
        if ("nexus_core" in fa or "trading_intelligence" in fa) and "payment_settlement" in ta:
            errors.append("AI/trading intelligence must not directly authorize settlement")

    by_id={c["contract_id"]:c for c in contracts["contracts"]}
    accounting=by_id["synergy.accounting.recognition/v1"]
    if accounting["producer"]!="Shtenco/synergy_financial_os":
        errors.append("accounting contract producer authority drift")
    settlement=by_id["synergy.settlement.evidence/v1"]
    if settlement["producer"]!="Shtenco/synergy_pay_system":
        errors.append("settlement contract producer authority drift")

    for c in contracts["contracts"]:
        if c["authority"]=="presentation":
            errors.append(f"presentation may not be canonical contract authority: {c['contract_id']}")

    known={x["id"] for x in inv["invariants"]}
    if len(known)!=len(inv["invariants"]):
        errors.append("duplicate invariant ids")

    if errors:
        for e in errors: print("ERROR:",e)
        raise SystemExit(1)

    print(f"OK: {len(inv['invariants'])} machine-checkable architecture invariants")
    print(f"OK: {len(runtime)} runtime dependency edges satisfy current hard policies")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
