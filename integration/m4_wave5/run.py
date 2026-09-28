#!/usr/bin/env python3
from __future__ import annotations
import hashlib,importlib.util,json,os,platform,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone

HERE=Path(__file__).resolve().parent
ROOT=Path(os.environ.get("SYNERGY_REPOS_ROOT",".")).resolve()
LOCK=json.loads((HERE/"integration_lock_v1.json").read_text(encoding="utf-8"))
W=[]

def repo(name):
    p=ROOT/name
    if not p.is_dir(): raise RuntimeError(f"missing repo: {p}")
    return p

def load(path,name):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);assert s and s.loader;s.loader.exec_module(m);return m

def check_lock():
    if os.environ.get("SYNERGY_VERIFY_LOCK","0")!="1": return
    for item in LOCK["repositories"]:
        name=item["repo"].split("/",1)[1]
        actual=subprocess.check_output(["git","rev-parse","HEAD"],cwd=repo(name),text=True).strip()
        if actual!=item["commit"]: raise RuntimeError(f"{name}: {actual} != {item['commit']}")

def witness(source,cid,evidence):
    W.append({"from":f"Shtenco/{source}","to":"Shtenco/synergy_meta_os","contract_id":cid,"evidence":evidence})

def main():
    check_lock();results=[];ok=True
    meta=load(repo("synergy_meta_os")/"runtime"/"app_release_contracts.py","meta_app")
    try:
        app=load(repo("synergy_app")/"federation"/"release_contract.py","app_release")
        p=app.store_source_evidence_payload()
        x=meta.consume_store_source_evidence(p)
        assert x["source_verified"] is True and x["artifact_built"] is False
        witness("synergy_app","synergy.app.store-source-evidence/v1","Meta-OS consumed exact source verification hashes without build/publication promotion")
        results.append({"name":"store-source","status":"PASS","error":None})
    except Exception as e:
        ok=False;results.append({"name":"store-source","status":"FAIL","error":repr(e)})
    try:
        sup=load(repo("sinergy_super_app")/"federation"/"surface_contract.py","super_surface")
        p=sup.superapp_surface_payload()
        x=meta.consume_superapp_surface(p)
        assert x["source_surface_verified"] is True and x["android_artifact_built"] is False
        witness("sinergy_super_app","synergy.app.superapp-surface/v1","Meta-OS consumed exact super-app source surface hashes without deployment promotion")
        results.append({"name":"superapp-surface","status":"PASS","error":None})
    except Exception as e:
        ok=False;results.append({"name":"superapp-surface","status":"FAIL","error":repr(e)})
    unique={(x["from"],x["to"],x["contract_id"]) for x in W}
    if len(W)!=2 or len(unique)!=2: ok=False
    evidence={"schema":"synergy.m4-wave5-evidence/v1","generated_at":datetime.now(timezone.utc).isoformat(),
      "lock_sha256":hashlib.sha256((HERE/"integration_lock_v1.json").read_bytes()).hexdigest(),
      "lock_repository_count":len(LOCK["repositories"]),"python":sys.version,"platform":platform.platform(),
      "results":results,"edge_witnesses":W,"edge_witness_count":len(W),"all_pass":ok}
    outdir=HERE/"evidence";outdir.mkdir(exist_ok=True)
    out=outdir/"m4_wave5_result.json";out.write_text(json.dumps(evidence,indent=2,sort_keys=True),encoding="utf-8")
    print("EVIDENCE",out)
    if not ok:return 1
    print("SYNERGY M4 WAVE5 E2E: PASS");return 0
if __name__=="__main__":raise SystemExit(main())
