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

HERE=Path(__file__).resolve().parent
ROOT=Path(os.environ.get("SYNERGY_REPOS_ROOT",".")).resolve()
LOCK=json.loads((HERE/"integration_lock_v1.json").read_text(encoding="utf-8"))
WITNESSES=[]


def repo(name:str)->Path:
    p=ROOT/name
    if not p.is_dir():
        raise RuntimeError(f"missing repo: {p}")
    return p


def load(path:Path,name:str):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def check_lock()->None:
    if os.environ.get("SYNERGY_VERIFY_LOCK","0")!="1":
        return
    for item in LOCK["repositories"]:
        name=item["repo"].split("/",1)[1]
        actual=subprocess.check_output(["git","rev-parse","HEAD"],cwd=repo(name),text=True).strip()
        if actual!=item["commit"]:
            raise RuntimeError(f"{name}: {actual} != locked {item['commit']}")


def witness(source:str,contract_id:str,evidence:str)->None:
    WITNESSES.append({
        "from":f"Shtenco/{source}",
        "to":"Shtenco/synergy_midas_ai",
        "contract_id":contract_id,
        "evidence":evidence,
    })


def main()->int:
    check_lock()
    midas=load(repo("synergy_midas_ai")/"contracts"/"m4_market_advisory_v1.py","m4_midas")
    results=[]
    all_pass=True

    cases=[]

    def marketvision():
        sys.path.insert(0,str(repo("synergy_marketvision")/"src"))
        from synergy_marketvision.synergy_contracts import market_features_payload
        bars=[
            {"open":1+i*.001,"high":1.01+i*.001,"low":.99+i*.001,"close":1+i*.001,"volume":100+i}
            for i in range(64)
        ]
        payload=market_features_payload(symbol="EURUSD",bars=bars,window=64,observation_id="m4-obs")
        consumed=midas.consume_market_features(payload)
        assert consumed["features"]["shape"]==[3,64,4]
        assert consumed["authorization"] is False
        witness("synergy_marketvision","synergy.trading.market-features/v1","MIDAS consumed exact MarketVision feature payload")
    cases.append(("market-features",marketvision))

    def adaptive():
        sys.path.insert(0,str(repo("synergy_adaptive_engine")/"src"))
        from synergy_adaptive_engine.synergy_contracts import market_regime_payload
        payload=market_regime_payload(
            symbol="EURUSD",
            returns=[.001,-.001,.002,-.002,.001,.0],
            observation_id="m4-obs",
        )
        consumed=midas.consume_market_regime(payload)
        assert consumed["regime"]==payload["regime"]
        assert consumed["authorization"] is False
        witness("synergy_adaptive_engine","synergy.trading.market-regime/v1","MIDAS consumed exact Adaptive Engine regime payload")
    cases.append(("market-regime",adaptive))

    def graph():
        sys.path.insert(0,str(repo("synergy_market_graph")/"src"))
        from synergy_market_graph.synergy_contracts import fair_value_payload
        payload=fair_value_payload(
            observation_id="m4-obs",
            src="EUR",dst="USD",
            edges=[
                {"src":"EUR","dst":"USD","rate":1.1,"fee_bps":1.0},
                {"src":"EUR","dst":"GBP","rate":.86,"fee_bps":1.0},
                {"src":"GBP","dst":"USD","rate":1.28,"fee_bps":1.0},
            ],
        )
        consumed=midas.consume_fair_value(payload)
        assert consumed["fair_value"]==payload["fair_value"]
        assert consumed["authorization"] is False
        witness("synergy_market_graph","synergy.trading.fair-value/v1","MIDAS consumed exact Market Graph fair-value payload")
    cases.append(("fair-value",graph))

    def maker():
        sys.path.insert(0,str(repo("synergy_market_maker")/"src"))
        from synergy_market_maker.synergy_contracts import liquidity_quote_payload
        payload=liquidity_quote_payload(
            observation_id="m4-obs",symbol="EURUSD",mid=1.1,inventory=0,sigma=.1
        )
        consumed=midas.consume_liquidity_quote(payload)
        assert consumed["status"]=="QUOTE"
        assert consumed["bid"]<consumed["ask"]
        assert consumed["authorization"] is False
        witness("synergy_market_maker","synergy.trading.liquidity-quote/v1","MIDAS consumed exact Market Maker quote payload")
    cases.append(("liquidity-quote",maker))

    def committee():
        sys.path.insert(0,str(repo("synergy_ai_investment_committee")/"src"))
        from synergy_ai_committee.synergy_contracts import investment_thesis_payload
        payload=investment_thesis_payload(
            observation_id="m4-obs",symbol="EURUSD",
            momentum=.4,volatility=.05,valuation=0,liquidity=1,
        )
        consumed=midas.consume_investment_thesis(payload)
        assert consumed["action"]==payload["action"]
        assert consumed["authorization"] is False
        assert consumed["requires_domain_validation"] is True
        witness("synergy_ai_investment_committee","synergy.trading.investment-thesis/v1","MIDAS consumed exact Investment Committee thesis payload")
    cases.append(("investment-thesis",committee))

    for name,fn in cases:
        try:
            fn()
            print("PASS",name)
            results.append({"name":name,"status":"PASS","error":None})
        except Exception as exc:
            all_pass=False
            print("FAIL",name,repr(exc))
            results.append({"name":name,"status":"FAIL","error":repr(exc)})

    unique={(x["from"],x["to"],x["contract_id"]) for x in WITNESSES}
    if len(WITNESSES)!=5 or len(unique)!=5:
        all_pass=False

    lock_bytes=(HERE/"integration_lock_v1.json").read_bytes()
    evidence={
        "schema":"synergy.m4-market-advisory-evidence/v1",
        "generated_at":datetime.now(timezone.utc).isoformat(),
        "lock_sha256":hashlib.sha256(lock_bytes).hexdigest(),
        "lock_repository_count":len(LOCK["repositories"]),
        "python":sys.version,
        "platform":platform.platform(),
        "results":results,
        "edge_witnesses":WITNESSES,
        "edge_witness_count":len(WITNESSES),
        "all_pass":all_pass,
    }
    outdir=HERE/"evidence"
    outdir.mkdir(exist_ok=True)
    out=outdir/"m4_market_advisory_result.json"
    out.write_text(json.dumps(evidence,indent=2,sort_keys=True),encoding="utf-8")
    print("EVIDENCE",out)
    if not all_pass:
        return 1
    print("SYNERGY M4 MARKET ADVISORY E2E: PASS")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
