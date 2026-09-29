#!/usr/bin/env python3
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
MANIFEST=HERE/"evidence_manifest_v1.json"
INTERFACES=ROOT/"registry"/"REPOSITORY_INTERFACES.json"

ACTIVE={"ADAPTER_IMPLEMENTED","E2E_TESTED","DEPLOYED"}

def load(path:Path):
    return json.loads(path.read_text(encoding="utf-8"))

def edge_set(scope_path:Path):
    d=load(scope_path)
    edges={(x["from"],x["to"],x["contract_id"]) for x in d.get("edges",[])}
    declared=d.get("edge_count")
    if declared != len(edges):
        raise ValueError(f"{scope_path}: declared edge_count={declared}, unique={len(edges)}")
    return edges

def registry_edges():
    d=load(INTERFACES)
    edges=set()
    for r in d.get("repositories",[]):
        for e in r.get("runtime_out",[]):
            if e.get("status") in ACTIVE:
                edges.add((r["repo"],e["to"],e["contract_id"]))
    return edges

def main()->int:
    manifest=load(MANIFEST)
    if manifest.get("schema")!="synergy.m5-observed-execution-manifest/v1":
        print("M5 OBSERVED EXECUTION: FAIL - manifest schema")
        return 1

    suites=manifest.get("suites",[])
    union=set()
    total=0
    errors=[]
    for suite in suites:
        scope=ROOT/suite["scope"]
        verifier=ROOT/suite["verifier"]
        evidence=ROOT/suite["evidence"]
        try:
            edges=edge_set(scope)
        except Exception as exc:
            errors.append(f"{suite['id']}: invalid scope: {exc}")
            continue
        if len(edges)!=suite.get("edge_count"):
            errors.append(f"{suite['id']}: manifest/scope edge count mismatch")
        overlap=union & edges
        if overlap:
            errors.append(f"{suite['id']}: duplicate scoped edges: {sorted(overlap)}")
        union |= edges
        total += len(edges)

        if not evidence.is_file():
            errors.append(f"{suite['id']}: observed evidence missing")
            continue
        proc=subprocess.run([sys.executable,str(verifier)],cwd=ROOT,text=True,capture_output=True)
        if proc.returncode!=0:
            errors.append(f"{suite['id']}: verifier failed: {(proc.stdout+proc.stderr).strip()}")

    expected=manifest.get("required_runtime_edges")
    if total!=expected or len(union)!=expected:
        errors.append(f"suite coverage mismatch: total={total} unique={len(union)} expected={expected}")

    reg=registry_edges()
    if union!=reg:
        errors.append(f"scope/registry mismatch: missing_from_scopes={sorted(reg-union)} extra_in_scopes={sorted(union-reg)}")

    if errors:
        print("M5 OBSERVED EXECUTION: NOT VERIFIED")
        for e in errors:
            print("-",e)
        print("verified_runtime_edges",0)
        return 1

    print("M5 OBSERVED EXECUTION: VERIFIED")
    print("verified_runtime_edges",len(union))
    print("promotion_target","E2E_TESTED")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
