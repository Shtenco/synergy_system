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
from uuid import uuid4

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
        sys.path.insert(0,str(repo("synergy_midas_institutional")/"src"))
        from synergy_midas.core import Signal, MidasOrchestrator
        from synergy_midas.synergy_contracts import institutional_assessment_payload
        midas=load(repo("synergy_midas_ai")/"contracts"/"m4_market_advisory_v1.py","m4_midas_w2")
        sig=Signal("m4w2","EURUSD","BUY",.72,.02,1000)
        decision=MidasOrchestrator(lambda s: True,lambda s:s.target_notional).decide(sig)
        payload=institutional_assessment_payload(signal=sig,decision=decision)
        consumed=midas.consume_institutional_assessment(payload)
        assert consumed["authorization"] is False
        witness("synergy_midas_institutional","synergy_midas_ai","synergy.trading.institutional-assessment/v1","MIDAS consumed exact Institutional assessment payload")
        results.append({"name":"institutional-assessment","status":"PASS","error":None})
    except Exception as e:
        ok=False; results.append({"name":"institutional-assessment","status":"FAIL","error":repr(e)})

    try:
        sys.path.insert(0,str(repo("synergy_crypto_pump")/"src"))
        from crypto_pump.synergy_contracts import crypto_anomaly_score_payload
        midas=load(repo("synergy_midas_ai")/"contracts"/"m4_market_advisory_v1.py","m4_midas_w2b")
        payload=crypto_anomaly_score_payload(
            observation_id="pump-obs",timestamp="2026-09-29T00:00:00Z",symbol="BTCUSDT",
            pump_probability=.81,rank=1,model_ref="pump-v1",feature_snapshot_sha256="1"*64
        )
        consumed=midas.consume_crypto_anomaly_score(payload)
        assert consumed["authorization"] is False
        witness("synergy_crypto_pump","synergy_midas_ai","synergy.trading.crypto-anomaly-score/v1","MIDAS consumed exact Crypto Pump anomaly score")
        results.append({"name":"crypto-anomaly","status":"PASS","error":None})
    except Exception as e:
        ok=False; results.append({"name":"crypto-anomaly","status":"FAIL","error":repr(e)})

    try:
        bridge=load(repo("synergy_2chain_qe")/"federation"/"bridge_health_contract.py","bridge_health")
        financial=load(repo("synergy_financial_os")/"contracts"/"research_inputs_v1.py","fos_research")
        payload=bridge.bridge_health_payload(
            observation_id="bridge-obs",locked_usdc=1_000_000,locked_eth=10**18,
            minted_usds=900_000,minted_eths=10**18,health_factor_bps=18000,emergency_stopped=False
        )
        consumed=financial.consume_bridge_health(payload)
        assert consumed["canonical_accounting"] is False
        witness("synergy_2chain_qe","synergy_financial_os","synergy.economy.bridge-health/v1","Financial OS consumed exact read-only bridge health telemetry")
        results.append({"name":"bridge-health","status":"PASS","error":None})
    except Exception as e:
        ok=False; results.append({"name":"bridge-health","status":"FAIL","error":repr(e)})

    try:
        sys.path.insert(0,str(repo("synergy_blochain_budget")/"src"))
        from synergy_budget.models import BudgetRecord
        from synergy_budget.synergy_contracts import budget_proof_payload
        rec=BudgetRecord(record_type="appropriation",budget_year=2026,amount_kopecks=10000,currency="RUB",dimensions={"program":"m4"},source={"url":"fixture:m4"}).payload()
        payload=budget_proof_payload(dataset_id="RU-DEMO",snapshot_id="snap-m4",records=[rec],as_of="2026-09-29")
        out=subprocess.check_output([
            "cargo","run","--quiet","--example","federation_budget_proof_consumer","--",
            payload["dataset_id"],payload["snapshot_id"],payload["record_merkle_root"],str(payload["record_count"])
        ],cwd=repo("synergy_ai_blockchain"),text=True)
        assert out.strip().startswith("PASS ")
        witness("synergy_blochain_budget","synergy_ai_blockchain","synergy.economy.budget-proof/v1","Rust blockchain consumer verified exact Budget Merkle root")
        results.append({"name":"budget-proof","status":"PASS","error":None})
    except Exception as e:
        ok=False; results.append({"name":"budget-proof","status":"FAIL","error":repr(e)})

    try:
        sys.path.insert(0,str(repo("synergy_ai_financial_system")/"simulation"))
        from aicb_scenario_evidence_v1 import AICBScenarioEvidence
        scenario=load(repo("synergy_ai_financial_system")/"simulation"/"synergy_contracts.py","scenario_contract")
        financial=load(repo("synergy_financial_os")/"contracts"/"research_inputs_v1.py","fos_research2")
        evidence=AICBScenarioEvidence(
            scenario_id="stress-m4",status="STRESS",model_sha256="1"*64,config_sha256="2"*64,
            seed=7,horizon_months=12,calibration_status="TEST",assumptions={"shock":.2},outputs={"nav":[1,.9]}
        )
        payload=scenario.scenario_evidence_payload(evidence)
        consumed=financial.consume_scenario_evidence(payload)
        assert consumed["canonical_accounting"] is False
        witness("synergy_ai_financial_system","synergy_financial_os","synergy.economy.scenario-evidence/v1","Financial OS consumed exact non-canonical scenario evidence")
        results.append({"name":"scenario-evidence","status":"PASS","error":None})
    except Exception as e:
        ok=False; results.append({"name":"scenario-evidence","status":"FAIL","error":repr(e)})

    unique={(x["from"],x["to"],x["contract_id"]) for x in W}
    if len(W)!=5 or len(unique)!=5: ok=False
    ev={
      "schema":"synergy.m4-wave2-evidence/v1",
      "generated_at":datetime.now(timezone.utc).isoformat(),
      "lock_sha256":hashlib.sha256((HERE/"integration_lock_v1.json").read_bytes()).hexdigest(),
      "lock_repository_count":len(LOCK["repositories"]),
      "python":sys.version,"platform":platform.platform(),
      "results":results,"edge_witnesses":W,"edge_witness_count":len(W),"all_pass":ok
    }
    outdir=HERE/"evidence";outdir.mkdir(exist_ok=True)
    out=outdir/"m4_wave2_result.json";out.write_text(json.dumps(ev,indent=2,sort_keys=True),encoding="utf-8")
    print("EVIDENCE",out)
    if not ok:return 1
    print("SYNERGY M4 WAVE2 E2E: PASS")
    return 0

if __name__=="__main__": raise SystemExit(main())
