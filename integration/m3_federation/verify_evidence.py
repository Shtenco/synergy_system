#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
EVIDENCE=HERE/"evidence"/"m3_federation_result.json"
LOCK=HERE/"integration_lock_v1.json"
EXPECTED={"science","engineering","real-economy","runtime-network","trust-ui"}

def main():
    if not EVIDENCE.is_file():
        print("ERROR: evidence file missing");return 1
    data=json.loads(EVIDENCE.read_text(encoding="utf-8"))
    if data.get("schema")!="synergy.m3-federation-evidence/v1":
        print("ERROR: schema mismatch");return 1
    lock_hash=hashlib.sha256(LOCK.read_bytes()).hexdigest()
    if data.get("lock_sha256")!=lock_hash:
        print("ERROR: lock hash mismatch");return 1
    if data.get("lock_repository_count")!=20:
        print("ERROR: lock repository count mismatch");return 1
    results=data.get("results")
    if not isinstance(results,list) or {x.get("name") for x in results}!=EXPECTED:
        print("ERROR: vertical set mismatch");return 1
    if len(results)!=len(EXPECTED):
        print("ERROR: duplicate/missing vertical result");return 1
    if not data.get("all_pass") or any(x.get("status")!="PASS" for x in results):
        print("ERROR: M3 evidence is not all-pass");return 1
    print("M3 FEDERATION EVIDENCE: VERIFIED")
    print("lock_sha256",lock_hash)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
