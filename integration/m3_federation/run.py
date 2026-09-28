#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from uuid import UUID

HERE=Path(__file__).resolve().parent
ROOT=Path(os.environ.get("SYNERGY_REPOS_ROOT",".")).resolve()
LOCK=json.loads((HERE/"integration_lock_v1.json").read_text(encoding="utf-8"))

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

def check_lock():
    if os.environ.get("SYNERGY_VERIFY_LOCK","0")!="1":
        return
    for item in LOCK["repositories"]:
        name=item["repo"].split("/",1)[1]
        actual=subprocess.check_output(["git","rev-parse","HEAD"],cwd=repo(name),text=True).strip()
        if actual!=item["commit"]:
            raise RuntimeError(f"{name}: {actual} != locked {item['commit']}")

def science_path():
    nexus=load(repo("synergy_agi_nexus")/"contracts"/"ai_proposal_v1.py","nexus_contract")
    sci=load(repo("synergy_nexus_science_agent")/"contracts"/"science_contracts.py","science_contract")
    mega=load(repo("synergy_megaproject")/"tools"/"science_contracts.py","mega_science")
    proposal=nexus.ai_proposal_payload(
        proposal_id=UUID("11111111-1111-4111-8111-111111111111"),
        task_type="SCIENCE",model_id="nexus-v18:m3",
        proposal={"question":"Does deterministic M3 evidence binding reproduce?"},
        confidence=.61,limitations=["proposal only; independent evidence required"]
    )
    task=sci.science_task_from_nexus(proposal)
    assert task["authorization"] is False
    src=sci.source_record(source_id="S-M3",locator="fixture:m3",content=b"measured fixture")
    package=sci.evidence_package_payload(
        research_question=proposal["proposal"]["question"],
        claims=[{"claim_id":"C-M3","text":"fixture was measured","epistemic_status":"MEASURED","source_ids":["S-M3"]}],
        sources=[src],status="REPRODUCED",reproduction_command="python m3_fixture.py"
    )
    queue=mega.science_package_to_review_queue(package)
    assert queue["canonical_graph_mutation"] is False
    assert queue["claim_review_queue"][0]["proposed_relation_type"]=="VALIDATES"

def engineering_path():
    sys.path.insert(0,str(repo("synergy_ai_language")/"src"))
    from ai_language.semantic_trace import build_semantic_trace
    from ai_language.synergy_contracts import requirement_trace_payload
    coder=load(repo("synergy_ai_coder")/"runtime"/"contracts.py","coder_contract")
    meta=load(repo("synergy_meta_os")/"runtime"/"change_contracts.py","meta_change")
    trace=build_semantic_trace("Implement typed boundary",["runtime/contracts.py"])
    req=trace.requirements[0]
    trace.record("write_file",{"path":"runtime/contracts.py","requirement_ids":[req.id]},"OK: wrote")
    trace.record("run_command",{"command":"pytest","requirement_ids":[req.id]},"OK: pass")
    payload=requirement_trace_payload(trace,affected_repositories=["Shtenco/synergy_ai_coder"])[0]
    consumed=coder.consume_requirement_trace(payload,target_repository="Shtenco/synergy_ai_coder")
    assert consumed["requirement_id"]==req.id
    change=coder.change_evidence_payload(
        change_id=UUID("22222222-2222-4222-8222-222222222222"),
        repository="Shtenco/synergy_ai_coder",commit_sha="1"*40,
        requirements=[req.id],checks=[coder.check_record(name="pytest",passed=True,evidence_bytes=b"PASS")],
        review_status="APPROVED",artifact_bytes=b"artifact"
    )
    meta.require_deployable_change(change,expected_repository="Shtenco/synergy_ai_coder")

def real_economy_path():
    e=load(repo("synergy_eurasian")/"interfaces"/"synergy_contracts.py","eurasian_contract")
    gov=load(repo("synergy_project")/"contracts"/"capital_governance_v1.py","capital_gov")
    sys.path.insert(0,str(repo("synergy_pay_system")/"src"))
    from synergy_pay.synergy_contracts import payment_intent_from_funding_authorization
    project=json.loads((repo("synergy_eurasian")/"examples"/"project_proposal_ai_agro.json").read_text(encoding="utf-8"))
    p=e.federation_project_proposal_payload(project)
    gov.validate_project_proposal(p)
    auth=gov.funding_authorization_payload(
        project_event_id=UUID("33333333-3333-4333-8333-333333333333"),
        authorization_id=UUID("44444444-4444-4444-8444-444444444444"),
        decision="AUTHORIZE",max_amount="100",currency="USD",
        authorized_rails=["bank"],expires_at=datetime.now(timezone.utc)+timedelta(hours=1),
        conditions=["M1"],approver_refs=["committee:1"],underwriting_evidence_ids=["evidence:m3"],policy_version="gov-m3"
    )
    intent=payment_intent_from_funding_authorization(auth,payer="treasury",payee="spv",amount="80")
    assert intent.amount==Decimal("80")

def runtime_network_path():
    compress=load(repo("synegy_ai_compress")/"compression_lab"/"synergy_contracts.py","compress_contract")
    net=load(repo("synergy_net")/"runtime"/"synergy_contracts.py","net_contract")
    sys.path.insert(0,str(repo("synergy_meta_os")))
    from runtime.transport_contracts import require_transport_delivery
    from runtime.synergy_contracts import node_manifest_payload
    turbo=load(repo("synergy_turbo_linux")/"turbo_orchestrator"/"synergy_contracts.py","turbo_contract")
    source=b"m3-content"*32
    archive=b"archive-m3"
    ae=compress.archive_evidence_payload(source=source,archive=archive,restored=source,codec_id="m3-codec")
    content=net.consume_archive_evidence(ae)
    assert content["content_id"]==ae["source_sha256"]
    te=net.transport_evidence_payload(
        session_id="m3",sender_peer="node-a",receiver_peer="node-b",content=archive,
        delivered_at=datetime.now(timezone.utc),transport_profile="authenticated-test",
        authenticated=True,route=["node-a","node-b"],bytes_on_wire=len(archive)+16,latency_ms=1.0
    )
    require_transport_delivery(te)
    blockchain=repo("synergy_ai_blockchain")
    out=subprocess.check_output([
        "cargo","run","--quiet","--example","federation_transport_consumer","--",
        te["session_id"],te["sender_peer"],te["receiver_peer"],te["content_sha256"],
        "true" if te["authenticated"] else "false",",".join(te["route"]),
        str(te["bytes_on_wire"]),str(te["latency_ms"])
    ],cwd=blockchain,text=True)
    assert out.strip().startswith("PASS ")
    with tempfile.TemporaryDirectory() as td:
        root=Path(td);artifact=root/"svc";artifact.write_bytes(b"svc")
        import hashlib
        manifest={
          "schema":1,"node_id":"m3-node","profile":"EDGE_CLIENT","attested":False,"development":True,"generation":1,
          "services":[{"name":"ui","role":"EDGE_CLIENT","artifact":"svc","sha256":hashlib.sha256(b"svc").hexdigest(),
          "argv":["$ARTIFACT"],"capabilities":["storage.read","ui.present"],
          "limits":{"memory_mib":64,"cpu_seconds":10,"open_files":32}}]
        }
        mp=root/"manifest.json";mp.write_text(json.dumps(manifest),encoding="utf-8")
        node=node_manifest_payload(mp,root)
        host=turbo.consume_node_manifest(node)
        assert host["host_authority"] is False

def trust_ui_path():
    financial=load(repo("synergy_financial_os")/"contracts"/"accounting_recognition_v1.py","financial_contract")
    apps=load(repo("synergy_apps")/"runtime"/"read_models.py","apps_contract")
    accounting=financial.accounting_recognition_payload(
        source_settlement_event_id=UUID("55555555-5555-4555-8555-555555555555"),
        recognition_id=UUID("66666666-6666-4666-8666-666666666666"),
        classification="ASSET_TRANSFER",
        entries=[
            {"account":"asset:bank","side":"DEBIT","asset":"USD","amount":"80"},
            {"account":"clearing:project","side":"CREDIT","asset":"USD","amount":"80"},
        ],
        recognized_at=datetime.now(timezone.utc),accounting_period="2026-09",
        hardnav_delta="0",settlement_payload={"status":"SETTLED","reconciled":True,"reconciliation_breaks":[]}
    )
    view_accounting=apps.accounting_read_model(accounting)
    assert view_accounting["read_only"] is True
    blockchain=repo("synergy_ai_blockchain")
    raw=subprocess.check_output(["cargo","run","--quiet","--example","federation_trust_fixture"],cwd=blockchain,text=True)
    trust=json.loads(raw.strip().splitlines()[-1])
    meta=load(repo("synergy_metachain")/"runtime"/"trust_contracts.py","metachain_contract")
    state=meta.CommitmentReplayState()
    claim=state.consume(trust)
    assert claim["claimable_once"] is True
    view=apps.trust_read_model(trust)
    assert view["read_only"] is True
    subprocess.run(["cargo","test","federation_contracts","--lib","--quiet"],cwd=blockchain,check=True)

def main():
    check_lock()
    science_path();print("PASS science")
    engineering_path();print("PASS engineering")
    real_economy_path();print("PASS real-economy")
    runtime_network_path();print("PASS runtime-network")
    trust_ui_path();print("PASS trust-ui")
    print("SYNERGY M3 FEDERATION SEMANTIC E2E: PASS")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
