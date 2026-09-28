#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
E=HERE/"evidence"/"m4_wave2_result.json";L=HERE/"integration_lock_v1.json";S=HERE/"edge_scope_v1.json"
def main():
    if not E.is_file(): print("ERROR: evidence missing"); return 1
    d=json.loads(E.read_text()); scope=json.loads(S.read_text())
    if d.get("schema")!="synergy.m4-wave2-evidence/v1": print("ERROR: schema"); return 1
    if d.get("lock_sha256")!=hashlib.sha256(L.read_bytes()).hexdigest(): print("ERROR: lock"); return 1
    if d.get("lock_repository_count")!=8: print("ERROR: repo count"); return 1
    expected={(x["from"],x["to"],x["contract_id"]) for x in scope["edges"]}
    actual={(x.get("from"),x.get("to"),x.get("contract_id")) for x in d.get("edge_witnesses",[])}
    if scope.get("edge_count")!=5 or len(expected)!=5 or len(actual)!=5 or actual!=expected: print("ERROR: edge set"); return 1
    if len(d.get("results",[]))!=5 or any(x.get("status")!="PASS" for x in d["results"]): print("ERROR: results"); return 1
    if d.get("all_pass") is not True: print("ERROR: not all-pass"); return 1
    print("M4 WAVE2 EVIDENCE: VERIFIED"); return 0
if __name__=="__main__": raise SystemExit(main())
