#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"registry"/"DOCUMENTATION_QUALITY.json"

def main():
    d=json.loads(P.read_text(encoding="utf-8"))
    entries=d.get("entries",[])
    errors=[]
    if d.get("repository_count")!=75 or len(entries)!=75:
        errors.append("documentation registry must contain exactly 75 repositories")
    names=[x.get("repo") for x in entries]
    if len(set(names))!=75:
        errors.append("repository names must be unique")
    verified=[x for x in entries if x.get("status")=="VERIFIED"]
    if d.get("verified_count")!=len(verified):
        errors.append("verified_count mismatch")
    for x in verified:
        if not x.get("readme_sha"):
            errors.append(f"{x.get('repo')}: missing README SHA")
        if x.get("chars",0)<6500:
            errors.append(f"{x.get('repo')}: README too small for verified deep pass")
        if x.get("headings",0)<12:
            errors.append(f"{x.get('repo')}: too few sections for verified deep pass")
    pending=[x for x in entries if x.get("status")!="VERIFIED"]
    if errors:
        print("DOCUMENTATION QUALITY GATE: INVALID")
        for e in errors: print("-",e)
        return 1
    print("DOCUMENTATION QUALITY REGISTRY: VALID")
    print("verified",len(verified),"/ 75")
    print("pending",len(pending))
    if pending:
        print("DOCUMENTATION DEEP PASS: NOT YET 75/75 VERIFIED")
        return 2
    print("DOCUMENTATION DEEP PASS: 75/75 VERIFIED")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
