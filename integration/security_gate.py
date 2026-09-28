#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BLOCKERS=ROOT/"registry"/"SECURITY_BLOCKERS.json"
INTERFACES=ROOT/"registry"/"REPOSITORY_INTERFACES.json"

def main()->int:
    blockers=json.loads(BLOCKERS.read_text(encoding="utf-8"))
    interfaces=json.loads(INTERFACES.read_text(encoding="utf-8"))
    unresolved={x["repo"]:x for x in blockers["blockers"] if x["status"]!="RESOLVED"}
    violations=[]
    for repo in interfaces["repositories"]:
        name=repo["repo"]
        b=unresolved.get(name)
        if not b:
            continue
        if b.get("federation_promotion_blocked") and repo.get("interface_status")!="ARCHITECTURAL_ONLY":
            violations.append((name,"federation promotion blocked",repo.get("interface_status")))
        if b.get("deployment_blocked"):
            deployed=[]
            for e in repo.get("runtime_out",[])+repo.get("runtime_in",[]):
                if e.get("status")=="DEPLOYED":
                    deployed.append(e.get("contract_id"))
            if deployed:
                violations.append((name,"deployment blocked",deployed))
    if violations:
        print("SECURITY GATE: FAIL")
        for v in violations:
            print(v)
        return 1
    print("SECURITY GATE: PASS")
    print("unresolved_blockers",len(unresolved))
    print("deployment_blocked",sum(bool(x.get("deployment_blocked")) for x in unresolved.values()))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
