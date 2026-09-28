from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "contracts" / "python" / "synergy_contracts_v1.py"
spec = importlib.util.spec_from_file_location("synergy_contracts_v1", MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

TRACE = UUID("00000000-0000-4000-8000-000000000001")

def payload_hash(payload):
    raw=json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
    return sha256(raw).hexdigest()

def event(contract_id, event_id, producer, authority, payload, parents=()):
    return {
        "contract_id": contract_id,
        "schema_version": 1,
        "event_id": str(event_id),
        "trace_id": str(TRACE),
        "producer": producer,
        "authority": authority,
        "produced_at": datetime(2026,9,28,18,0,tzinfo=timezone.utc).isoformat(),
        "payload": payload,
        "payload_sha256": payload_hash(payload),
        "evidence_ids": [],
        "parent_event_ids": [str(x) for x in parents],
    }

def test_full_trading_truth_trace():
    p_id=UUID("10000000-0000-4000-8000-000000000001")
    p={
      "decision_id":str(UUID("11000000-0000-4000-8000-000000000001")),
      "as_of":"2026-09-28T18:00:00+00:00","account_id":"demo",
      "positions":[{"symbol":"EURUSD","side":"BUY","notional":"1000"}],
      "rationale":["frozen candidate"],"confidence":0.61,"model_refs":["midas:v1"],"market_state_id":"mkt-1"
    }
    e1=event("synergy.trading.portfolio-decision/v1",p_id,"Shtenco/synergy_midas_ai","trading_intelligence",p)
    mod.validate_typed_event(e1)

    v_id=UUID("20000000-0000-4000-8000-000000000001")
    v={"candidate_event_id":str(p_id),"gate":"CANARY","protocol_id":"purged-wf-v1",
       "dataset_manifest_sha256":"1"*64,
       "metrics":{"n":100,"total_return":0.04,"sharpe":0.8,"max_drawdown":0.05,"hit_rate":0.53},
       "warnings":[]}
    mod.validate_typed_event(event("synergy.trading.validation-decision/v1",v_id,"Shtenco/synergy_quantlab","trading_validation",v,[p_id]))

    r_id=UUID("30000000-0000-4000-8000-000000000001")
    r={"source_event_id":str(v_id),"action":"RESIZE","approved_notional":"750","reasons":[],
       "metrics":{"gross_exposure":0.4},"account_state_version":"acct-42","policy_version":"risk-2.0"}
    mod.validate_typed_event(event("synergy.trading.risk-decision/v1",r_id,"Shtenco/synergy_riskguard","trading_risk",r,[v_id]))

    x_id=UUID("40000000-0000-4000-8000-000000000001")
    x={"risk_event_id":str(r_id),"correlation_id":"route-1","symbol":"EURUSD","side":"BUY",
       "requested_notional":"750","slices":[{"venue":"paper","notional":"750","expected_price":"1.10","expected_cost_bps":2.0}],
       "unfilled_notional":"0"}
    mod.validate_typed_event(event("synergy.trading.execution-plan/v1",x_id,"Shtenco/synergy_trademux","trade_execution",x,[r_id]))

    f_id=UUID("50000000-0000-4000-8000-000000000001")
    f={"plan_event_id":str(x_id),"symbol":"EURUSD","side":"BUY","requested_notional":"750","filled_notional":"750",
       "fills":[{"venue":"paper","requested":"750","filled":"750","avg_price":"1.10","fee":"0.15","external_id":"fill-1"}],"status":"FILLED"}
    mod.validate_typed_event(event("synergy.trading.execution-result/v1",f_id,"Shtenco/synergy_trademux","trade_execution",f,[x_id]))

    s_id=UUID("60000000-0000-4000-8000-000000000001")
    s={"settlement_id":str(UUID("61000000-0000-4000-8000-000000000001")),"reference":"fill-1","asset":"USD","amount":"750",
       "provider":"paper","status":"SETTLED","occurred_at":"2026-09-28T18:01:00+00:00","reconciled":True,"reconciliation_breaks":[],"provider_reference":"fill-1"}
    mod.validate_typed_event(event("synergy.settlement.evidence/v1",s_id,"Shtenco/synergy_pay_system","payment_settlement",s,[f_id]))

    a_id=UUID("70000000-0000-4000-8000-000000000001")
    a={"source_settlement_event_id":str(s_id),"recognition_id":str(UUID("71000000-0000-4000-8000-000000000001")),
       "classification":"ASSET_TRANSFER","entries":[],"recognized_at":"2026-09-28T18:02:00+00:00","accounting_period":"2026-09-28",
       "hardnav_delta":"0","liquidnav_delta":"0","economicnav_delta":"0","policy_refs":["fos:v1"]}
    mod.validate_typed_event(event("synergy.accounting.recognition/v1",a_id,"Shtenco/synergy_financial_os","canonical_accounting",a,[s_id]))

    b_id=UUID("80000000-0000-4000-8000-000000000001")
    b={"source_event_id":str(a_id),"source_contract_id":"synergy.accounting.recognition/v1","payload_sha256":payload_hash(a),
       "chain_id":"synergy-dev","commitment_id":"commit-1","finality_status":"FINALIZED","block_height":1,"tx_id":"tx-1","authorization_profile":"PQ_ONLY"}
    mod.validate_typed_event(event("synergy.trust.commitment/v1",b_id,"Shtenco/synergy_ai_blockchain","blockchain_trust",b,[a_id]))
