#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, os, platform, subprocess, sys, tempfile
from pathlib import Path
from datetime import datetime, timezone

HERE=Path(__file__).resolve().parent
ROOT=Path(os.environ.get("SYNERGY_REPOS_ROOT",".")).resolve()
LOCK=json.loads((HERE/"integration_lock_v1.json").read_text(encoding="utf-8"))
W=[]

def repo(name:str)->Path:
    p=ROOT/name
    if not p.is_dir(): raise RuntimeError(f"missing repo: {p}")
    return p

def load(path:Path,name:str):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

def check_lock():
    if os.environ.get("SYNERGY_VERIFY_LOCK","0")!="1": return
    for item in LOCK["repositories"]:
        name=item["repo"].split("/",1)[1]
        actual=subprocess.check_output(["git","rev-parse","HEAD"],cwd=repo(name),text=True).strip()
        if actual!=item["commit"]: raise RuntimeError(f"{name}: {actual} != {item['commit']}")

def witness(source,target,cid,evidence):
    W.append({"from":f"Shtenco/{source}","to":f"Shtenco/{target}","contract_id":cid,"evidence":evidence})

def run_case(name,fn,results):
    try:
        fn(); print("PASS",name); results.append({"name":name,"status":"PASS","error":None}); return True
    except Exception as e:
        print("FAIL",name,repr(e)); results.append({"name":name,"status":"FAIL","error":repr(e)}); return False

def main()->int:
    check_lock(); results=[]; ok=True

    def xpu():
        sys.path.insert(0,str(repo("synergy_motherboard_xpu_xml")/"calculations"))
        from synergy_contracts import hardware_model_payload
        meta=load(repo("synergy_meta_os")/"runtime"/"hardware_model_contracts.py","meta_hw")
        payload=hardware_model_payload()
        consumed=meta.consume_hardware_model(payload)
        assert consumed["measured_silicon"] is False
        witness("synergy_motherboard_xpu_xml","synergy_meta_os","synergy.runtime.hardware-model/v1","Meta-OS consumed exact XPU analytical model output")
    ok=run_case("hardware-model",xpu,results) and ok

    def quantum():
        sys.path.insert(0,str(repo("binary_quantum_theory")/"scripts"))
        from synergy_contracts import quantum_reference_payload
        science=load(repo("synergy_nexus_science_agent")/"contracts"/"science_contracts.py","science_qm")
        payload=quantum_reference_payload(benchmark_id="wave4-chsh",trials=4)
        consumed=science.consume_quantum_reference_control(payload)
        assert consumed["novel_physics_claim"] is False
        witness("binary_quantum_theory","synergy_nexus_science_agent","synergy.science.quantum-reference-control/v1","Science Agent consumed exact standard-QM CHSH control")
    ok=run_case("quantum-reference",quantum,results) and ok

    def money():
        sys.path.insert(0,str(repo("synergy_graph_print_money")/"src"))
        from synergy_graph.synergy_contracts import monetary_simulation_payload
        financial=load(repo("synergy_financial_os")/"contracts"/"research_inputs_v1.py","financial_wave4")
        payload=monetary_simulation_payload(run_id="wave4-money",packets=3)
        consumed=financial.consume_monetary_simulation(payload)
        assert consumed["realized_external_pnl"] is False
        assert consumed["canonical_accounting"] is False
        witness("synergy_graph_print_money","synergy_financial_os","synergy.economy.monetary-simulation/v1","Financial OS consumed exact monetary simulation while refusing realized-PnL promotion")
    ok=run_case("monetary-simulation",money,results) and ok

    def graph():
        sys.path.insert(0,str(repo("epstein_network")/"src"))
        from epstein_network.synergy_contracts import provenance_graph_payload
        science=load(repo("synergy_nexus_science_agent")/"contracts"/"science_contracts.py","science_graph")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);vendor=root/"vendor";source=vendor/"fixture";source.mkdir(parents=True)
            (source/"records.json").write_text(json.dumps([
                {"name":"Example Person","email":"person@example.invalid"},
                {"from":"a@example.invalid","to":"b@example.invalid"}
            ]),encoding="utf-8")
            payload=provenance_graph_payload(snapshot_id="wave4-fixture",vendor=vendor,out=root/"out")
        consumed=science.consume_provenance_graph(payload)
        assert consumed["wrongdoing_inference_authority"] is False
        witness("epstein_network","synergy_nexus_science_agent","synergy.science.provenance-graph/v1","Science Agent consumed exact fixture provenance graph with inference authority disabled")
    ok=run_case("provenance-graph",graph,results) and ok

    def benchmark():
        sys.path.insert(0,str(repo("synergy_agi_olga")/"benchmarks"))
        from synergy_contracts import benchmark_suite_payload
        nexus=load(repo("synergy_agi_nexus")/"contracts"/"benchmark_suite_v1.py","nexus_bench")
        payload=benchmark_suite_payload(benchmark_run_id="wave4-suite")
        consumed=nexus.consume_benchmark_suite(payload)
        assert consumed["task_count"]==40
        assert consumed["agi_claim_authority"] is False
        witness("synergy_agi_olga","synergy_agi_nexus","synergy.ai.benchmark-suite/v1","NEXUS consumed exact deterministic 40-task benchmark manifest")
    ok=run_case("benchmark-suite",benchmark,results) and ok

    unique={(x["from"],x["to"],x["contract_id"]) for x in W}
    if len(W)!=5 or len(unique)!=5: ok=False
    evidence={
        "schema":"synergy.m4-wave4-evidence/v1",
        "generated_at":datetime.now(timezone.utc).isoformat(),
        "lock_sha256":hashlib.sha256((HERE/"integration_lock_v1.json").read_bytes()).hexdigest(),
        "lock_repository_count":len(LOCK["repositories"]),
        "python":sys.version,"platform":platform.platform(),
        "results":results,"edge_witnesses":W,"edge_witness_count":len(W),"all_pass":ok
    }
    outdir=HERE/"evidence";outdir.mkdir(exist_ok=True)
    out=outdir/"m4_wave4_result.json";out.write_text(json.dumps(evidence,indent=2,sort_keys=True),encoding="utf-8")
    print("EVIDENCE",out)
    if not ok:return 1
    print("SYNERGY M4 WAVE4 E2E: PASS")
    return 0

if __name__=="__main__": raise SystemExit(main())
