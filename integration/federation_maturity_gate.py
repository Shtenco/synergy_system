#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/"registry"

def load(name:str):
    return json.loads((REG/name).read_text(encoding="utf-8"))

def main()->int:
    interfaces=load("REPOSITORY_INTERFACES.json")
    contracts=load("CONTRACT_REGISTRY.json")
    gaps=load("INTEGRATION_GAPS.json")
    backlog=load("FEDERATION_BACKLOG.json")
    security=load("SECURITY_BLOCKERS.json")

    errors=[]
    repos=interfaces.get("repositories",[])
    if len(repos)!=75 or interfaces.get("repository_count")!=75:
        errors.append(f"repository count mismatch: {len(repos)} / {interfaces.get('repository_count')}")
    names=[r.get("repo") for r in repos]
    if len(set(names))!=75:
        errors.append("repository names are not unique")

    allowed=set(interfaces.get("interface_status_vocabulary",[]))
    if not allowed:
        errors.append("interface status vocabulary missing")
    unknown=[(r.get("repo"),r.get("interface_status")) for r in repos if r.get("interface_status") not in allowed]
    if unknown:
        errors.append(f"unknown interface statuses: {unknown}")
    unclassified=[r["repo"] for r in repos if r.get("interface_status")=="ARCHITECTURAL_ONLY"]
    if unclassified:
        errors.append(f"post-audit ARCHITECTURAL_ONLY remains: {unclassified}")

    contract_map={c["contract_id"]:c for c in contracts.get("contracts",[])}
    gap_map={c["contract_id"]:c for c in gaps.get("contracts",[])}
    if set(contract_map)!=set(gap_map):
        errors.append("CONTRACT_REGISTRY and INTEGRATION_GAPS contract-id sets differ")
    for cid,g in gap_map.items():
        if g.get("missing_endpoints"):
            errors.append(f"{cid}: missing endpoints remain")

    edge_count=0
    for r in repos:
        for e in r.get("runtime_out",[]):
            if e.get("status") not in {"ADAPTER_IMPLEMENTED","E2E_TESTED","DEPLOYED"}:
                continue
            edge_count+=1
            cid=e.get("contract_id")
            c=contract_map.get(cid)
            if not c:
                errors.append(f"{r['repo']} -> {e.get('to')}: unregistered contract {cid}")
                continue
            if c.get("producer")!=r["repo"]:
                errors.append(f"{cid}: producer mismatch {r['repo']} != {c.get('producer')}")
            if e.get("to") not in c.get("consumers",[]):
                errors.append(f"{cid}: consumer {e.get('to')} absent from contract registry")
            target=next((x for x in repos if x["repo"]==e.get("to")),None)
            if not target:
                errors.append(f"{cid}: target repo missing {e.get('to')}")
            elif not any(x.get("from")==r["repo"] and x.get("contract_id")==cid for x in target.get("runtime_in",[])):
                errors.append(f"{cid}: reciprocal runtime_in missing on {e.get('to')}")

    declared_edges=gaps.get("totals",{}).get("runtime_adapter_edges")
    if declared_edges!=edge_count:
        errors.append(f"runtime edge total mismatch: registry={edge_count}, gaps={declared_edges}")

    integrated={r["repo"] for r in repos if r.get("interface_status")=="ADAPTER_INTEGRATED"}
    non_integrated=set(names)-integrated
    backlog_entries=backlog.get("entries",[])
    backlog_names={x.get("repo") for x in backlog_entries}
    if backlog_names!=non_integrated:
        errors.append(f"backlog/non-integrated set mismatch: missing={sorted(non_integrated-backlog_names)} extra={sorted(backlog_names-non_integrated)}")
    if backlog.get("integrated_count")!=len(integrated) or backlog.get("non_integrated_count")!=len(non_integrated):
        errors.append("backlog integrated/non-integrated counters mismatch")
    if backlog.get("unclassified_count")!=0:
        errors.append("backlog unclassified_count must be zero after full maturity audit")

    blocked={x["repo"] for x in security.get("blockers",[]) if x.get("status")!="RESOLVED" and x.get("federation_promotion_blocked")}
    status_blocked={r["repo"] for r in repos if r.get("interface_status")=="SECURITY_BLOCKED"}
    if blocked!=status_blocked:
        errors.append(f"security blocker/status mismatch: blockers={sorted(blocked)} statuses={sorted(status_blocked)}")

    if errors:
        print("FEDERATION MATURITY GATE: FAIL")
        for e in errors:
            print("-",e)
        return 1

    counts={}
    for r in repos:
        counts[r["interface_status"]]=counts.get(r["interface_status"],0)+1
    print("FEDERATION MATURITY GATE: PASS")
    print("repositories",len(repos))
    print("contracts",len(contract_map))
    print("runtime_edges",edge_count)
    print("status_counts",json.dumps(counts,sort_keys=True))
    print("unclassified",0)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
