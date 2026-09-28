#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import platform
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
from decimal import Decimal

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

def main()->int:
    check_lock()
    results=[]; ok=True

    try:
        sys.path.insert(0,str(repo("synergy_relative_value")/"src"))
        from synergy_relative_value.synergy_contracts import relative_value_signal_payload
        midas=load(repo("synergy_midas_ai")/"contracts"/"m4_market_advisory_v1.py","midas_w3")
        x=[1+i*.01 for i in range(20)]
        y=[2+1.5*v for v in x]
        payload=relative_value_signal_payload(
            observation_id="rv-e2e",symbol_x="EURUSD",symbol_y="GBPUSD",
            x_history=x,y_history=y,x_now=x[-1],y_now=y[-1]+.1
        )
        consumed=midas.consume_relative_value_signal(payload)
        assert consumed["authorization"] is False
        witness("synergy_relative_value","synergy_midas_ai","synergy.trading.relative-value-signal/v1","MIDAS consumed the exact relative-value model output")
        results.append({"name":"relative-value","status":"PASS","error":None})
    except Exception as e:
        ok=False;results.append({"name":"relative-value","status":"FAIL","error":repr(e)})

    try:
        sys.path.insert(0,str(repo("synergy_agentic_ai_economy")))
        from agent_economy.models import ExecutionMandate
        from agent_economy.synergy_contracts import economy_simulation_payload
        nexus=load(repo("synergy_agi_nexus")/"contracts"/"agent_economy_context_v1.py","nexus_agent_economy")
        payload=economy_simulation_payload(
            run_id="agent-e2e",tick=42,active_agents=7,
            external_assets=Decimal("120"),internal_assets=Decimal("500"),external_revenue=Decimal("8"),
            mandate=ExecutionMandate(mode="simulation")
        )
        consumed=nexus.consume_agent_economy_simulation(payload)
        assert consumed["authorization"] is False
        witness("synergy_agentic_ai_economy","synergy_agi_nexus","synergy.agent.economy-simulation/v1","NEXUS consumed the exact bounded agent-economy simulation state")
        results.append({"name":"agent-economy","status":"PASS","error":None})
    except Exception as e:
        ok=False;results.append({"name":"agent-economy","status":"FAIL","error":repr(e)})

    try:
        proc=subprocess.run(
            [sys.executable,str(repo("dlp_solver")/"src"/"reverse_exp_exact_counts.py"),"1"],
            check=True,capture_output=True,text=True
        )
        measured=json.loads(proc.stdout)
        producer=load(repo("dlp_solver")/"src"/"synergy_contracts.py","dlp_contract")
        science=load(repo("synergy_nexus_science_agent")/"contracts"/"science_contracts.py","science_w3a")
        payload=producer.constraint_benchmark_payload(
            benchmark_id="reverse-exp-n1-k4",problem_family="SHA256-prefix",
            candidate_bits=8,constrained_bits=4,surviving_candidates=int(measured["counts"][4]),
            elapsed_s=float(measured["elapsed_s"]),method="exact-enumeration",
            reproducible_command="python src/reverse_exp_exact_counts.py 1"
        )
        consumed=science.consume_constraint_benchmark(payload)
        assert consumed["break_claim"] is False
        witness("dlp_solver","synergy_nexus_science_agent","synergy.science.constraint-benchmark/v1","Science Agent consumed measured exact-enumeration constraint evidence")
        results.append({"name":"constraint-benchmark","status":"PASS","error":None})
    except Exception as e:
        ok=False;results.append({"name":"constraint-benchmark","status":"FAIL","error":repr(e)})

    try:
        sys.path.insert(0,str(repo("synergy_cold_nuclear")/"models"))
        cold=load(repo("synergy_cold_nuclear")/"models"/"synergy_contracts.py","cold_contract")
        science=load(repo("synergy_nexus_science_agent")/"contracts"/"science_contracts.py","science_w3b")
        payload=cold.model_consistency_payload(
            experiment_id="cold-graph-e2e",max_abs_error=0.0,hypothesis_label="DERIVED",
            assumptions=["graph identity test is computational only","no observed nuclear effect is inferred"]
        )
        consumed=science.consume_model_consistency(payload)
        assert consumed["observed_physical_effect"] is False
        witness("synergy_cold_nuclear","synergy_nexus_science_agent","synergy.science.model-consistency/v1","Science Agent consumed the exact non-causal graph consistency evidence")
        results.append({"name":"model-consistency","status":"PASS","error":None})
    except Exception as e:
        ok=False;results.append({"name":"model-consistency","status":"FAIL","error":repr(e)})

    try:
        sys.path.insert(0,str(repo("synergy_qr_compress")))
        from qr_temporal.qtd3 import RepoBlob
        from qr_temporal.synergy_contracts import lossless_benchmark_payload
        sys.path.insert(0,str(repo("synergy_meta_os")))
        from runtime.archive_contracts import consume_archive_benchmark_evidence
        blobs=[RepoBlob("a.txt",1,b"alpha beta gamma\n"*20),RepoBlob("b.txt",2,b"alpha beta delta\n"*20)]
        target=b"alpha beta gamma\n"*19+b"fresh suffix\n"
        payload=lossless_benchmark_payload(
            benchmark_id="qtd3-e2e",training_blobs=blobs,target=target,path="a.txt",target_unix_ns=3
        )
        consumed=consume_archive_benchmark_evidence(payload)
        assert consumed["round_trip_verified"] is True
        witness("synergy_qr_compress","synergy_meta_os","synergy.archive.benchmark-evidence/v1","Meta-OS consumed exact QTD3 round-trip benchmark evidence")
        results.append({"name":"archive-benchmark","status":"PASS","error":None})
    except Exception as e:
        ok=False;results.append({"name":"archive-benchmark","status":"FAIL","error":repr(e)})

    unique={(x["from"],x["to"],x["contract_id"]) for x in W}
    if len(W)!=5 or len(unique)!=5: ok=False
    ev={
      "schema":"synergy.m4-wave3-evidence/v1",
      "generated_at":datetime.now(timezone.utc).isoformat(),
      "lock_sha256":hashlib.sha256((HERE/"integration_lock_v1.json").read_bytes()).hexdigest(),
      "lock_repository_count":len(LOCK["repositories"]),
      "python":sys.version,"platform":platform.platform(),
      "results":results,"edge_witnesses":W,"edge_witness_count":len(W),"all_pass":ok
    }
    outdir=HERE/"evidence";outdir.mkdir(exist_ok=True)
    out=outdir/"m4_wave3_result.json";out.write_text(json.dumps(ev,indent=2,sort_keys=True),encoding="utf-8")
    print("EVIDENCE",out)
    if not ok:return 1
    print("SYNERGY M4 WAVE3 E2E: PASS")
    return 0

if __name__=="__main__": raise SystemExit(main())
