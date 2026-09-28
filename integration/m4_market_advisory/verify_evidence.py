#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
EVIDENCE=HERE/"evidence"/"m4_market_advisory_result.json"
LOCK=HERE/"integration_lock_v1.json"
SCOPE=HERE/"edge_scope_v1.json"

def main()->int:
    if not EVIDENCE.is_file():
        print("ERROR: evidence missing")
        return 1
    data=json.loads(EVIDENCE.read_text(encoding="utf-8"))
    if data.get("schema")!="synergy.m4-market-advisory-evidence/v1":
        print("ERROR: schema mismatch"); return 1
    if data.get("lock_sha256")!=hashlib.sha256(LOCK.read_bytes()).hexdigest():
        print("ERROR: lock hash mismatch"); return 1
    if data.get("lock_repository_count")!=6:
        print("ERROR: lock repo count mismatch"); return 1
    scope=json.loads(SCOPE.read_text(encoding="utf-8"))
    expected={(x["from"],x["to"],x["contract_id"]) for x in scope["edges"]}
    witnesses=data.get("edge_witnesses") or []
    actual={(x.get("from"),x.get("to"),x.get("contract_id")) for x in witnesses}
    if scope.get("edge_count")!=5 or len(expected)!=5:
        print("ERROR: invalid scope"); return 1
    if len(witnesses)!=5 or actual!=expected:
        print("ERROR: edge witness mismatch")
        print("missing",sorted(expected-actual))
        print("extra",sorted(actual-expected))
        return 1
    results=data.get("results") or []
    expected_names={"market-features","market-regime","fair-value","liquidity-quote","investment-thesis"}
    if len(results)!=5 or {x.get("name") for x in results}!=expected_names:
        print("ERROR: result set mismatch"); return 1
    if any(x.get("status")!="PASS" for x in results) or data.get("all_pass") is not True:
        print("ERROR: M4 evidence is not all-pass"); return 1
    print("M4 MARKET ADVISORY EVIDENCE: VERIFIED")
    print("runtime_edges",len(expected))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
