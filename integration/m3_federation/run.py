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
import tempfile
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from uuid import UUID

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("SYNERGY_REPOS_ROOT", ".")).resolve()
LOCK = json.loads((HERE / "integration_lock_v1.json").read_text(encoding="utf-8"))
WITNESSES: list[dict[str, str]] = []
SHARED: dict[str, object] = {}


def repo(name: str) -> Path:
    p = ROOT / name
    if not p.is_dir():
        raise RuntimeError(f"missing repo: {p}")
    return p


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def witness(source: str, target: str, contract_id: str, evidence: str) -> None:
    WITNESSES.append({
        "from": f"Shtenco/{source}",
        "to": f"Shtenco/{target}",
        "contract_id": contract_id,
        "evidence": evidence,
    })


def canonical_json_bytes(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def check_lock() -> None:
    if os.environ.get("SYNERGY_VERIFY_LOCK", "0") != "1":
        return
    for item in LOCK["repositories"]:
        name = item["repo"].split("/", 1)[1]
        actual = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo(name), text=True
        ).strip()
        if actual != item["commit"]:
            raise RuntimeError(f"{name}: {actual} != locked {item['commit']}")


def dynamic_trust_commitment(accounting: dict) -> dict:
    raw = canonical_json_bytes(accounting)
    digest = hashlib.sha256(raw).hexdigest()
    source_event_id = str(accounting["recognition_id"])
    blockchain = repo("synergy_ai_blockchain")
    out = subprocess.check_output([
        "cargo", "run", "--quiet", "--example", "federation_accounting_consumer", "--",
        source_event_id,
        "synergy.accounting.recognition/v1",
        digest,
        "synergy-dev",
        "FINALIZED",
    ], cwd=blockchain, text=True)
    trust = json.loads(out.strip().splitlines()[-1])
    assert trust["payload_sha256"] == digest
    assert trust["source_event_id"] == source_event_id
    assert trust["source_contract_id"] == "synergy.accounting.recognition/v1"
    return trust


def trading_path() -> None:
    nexus = load(repo("synergy_agi_nexus") / "contracts" / "ai_proposal_v1.py", "nexus_trading")
    midas_advisory = load(repo("synergy_midas_ai") / "contracts" / "nexus_advisory_v1.py", "midas_advisory")
    midas_portfolio = load(repo("synergy_midas_ai") / "contracts" / "portfolio_decision_v1.py", "midas_portfolio")

    proposal = nexus.ai_proposal_payload(
        proposal_id=UUID("10000000-0000-4000-8000-000000000001"),
        task_type="TRADING",
        model_id="nexus-v18:m3",
        proposal={"symbol": "EURUSD", "thesis": "bounded candidate"},
        confidence=0.61,
        limitations=["advisory only; domain validation required"],
    )
    advisory = midas_advisory.nexus_advisory_context(proposal)
    assert advisory["authorization"] is False
    witness("synergy_agi_nexus", "synergy_midas_ai", "synergy.ai.proposal/v1", "nexus_advisory_context accepted the exact NEXUS proposal")

    portfolio = midas_portfolio.portfolio_decision_payload(
        decision_id=UUID("10000000-0000-4000-8000-000000000002"),
        as_of=datetime(2026, 9, 28, 18, 0, tzinfo=timezone.utc),
        account_id="m3-demo",
        positions=[{"symbol": "EURUSD", "side": "BUY", "notional": "1000"}],
        rationale=["candidate derived after NEXUS advisory"],
        confidence=advisory["confidence"],
        model_refs=[advisory["model_id"]],
        market_state_id="m3-market",
    )

    sys.path.insert(0, str(repo("synergy_quantlab") / "src"))
    from synergy_quantlab.synergy_contracts import validate_portfolio_candidate, validation_decision_payload
    validate_portfolio_candidate(portfolio)
    witness("synergy_midas_ai", "synergy_quantlab", "synergy.trading.portfolio-decision/v1", "QuantLab validated the exact MIDAS portfolio payload")
    validation = validation_decision_payload(
        candidate_event_id=portfolio["decision_id"],
        metrics={"n": 100, "total_return": 0.05, "sharpe": 0.8, "max_drawdown": 0.05, "hit_rate": 0.53},
        protocol_id="m3-purged-wf",
        dataset_manifest_sha256="1" * 64,
    )
    assert validation["gate"] in {"PAPER", "CANARY"}

    sys.path.insert(0, str(repo("synergy_riskguard") / "src"))
    from synergy_riskguard.core import AccountState, decide
    from synergy_riskguard.synergy_contracts import order_intent_from_validated_contracts, risk_decision_payload
    order = order_intent_from_validated_contracts(
        portfolio_payload=portfolio, validation_payload=validation
    )
    witness("synergy_quantlab", "synergy_riskguard", "synergy.trading.validation-decision/v1", "RiskGuard built an OrderIntent from the exact QuantLab validation payload")
    decision = decide(
        AccountState(
            equity=10000,
            start_day_equity=10000,
            high_watermark=10000,
            gross_exposure=0,
        ),
        order,
    )
    risk = risk_decision_payload(
        source_event_id=UUID("10000000-0000-4000-8000-000000000003"),
        decision=decision,
        account_state_version="m3-account",
        policy_version="m3-risk",
    )
    assert risk["action"] in {"ALLOW", "RESIZE"}

    sys.path.insert(0, str(repo("synergy_trademux") / "src"))
    from synergy_trademux.core import Fill, VenueQuote
    from synergy_trademux.synergy_contracts import plan_from_risk_decision, execution_result_payload
    plan = plan_from_risk_decision(
        risk_payload=risk,
        quotes=[VenueQuote("paper", 1.1, 1000, 1.0, 1.0, 5.0)],
        symbol="EURUSD",
        side="BUY",
    )
    assert sum(s.notional for s in plan.slices) > 0
    witness("synergy_riskguard", "synergy_trademux", "synergy.trading.risk-decision/v1", "TradeMux routed the exact allowed RiskGuard decision")
    execution = execution_result_payload(
        plan_event_id=UUID("10000000-0000-4000-8000-000000000004"),
        symbol="EURUSD",
        side="BUY",
        requested_notional=float(risk["approved_notional"]),
        fills=[Fill("paper", 1000, 1000, 1.1, 0.2, "m3-fill-1")],
        status="FILLED",
    )

    sys.path.insert(0, str(repo("synergy_pay_system") / "src"))
    from synergy_pay.synergy_contracts import expected_internal_evidence_from_execution_result, settlement_evidence_payload
    expected = expected_internal_evidence_from_execution_result(
        execution, asset="USD", occurred_at=datetime(2026, 9, 28, 18, 1, tzinfo=timezone.utc)
    )
    assert expected[0].reference == "m3-fill-1"
    witness("synergy_trademux", "synergy_pay_system", "synergy.trading.execution-result/v1", "Pay converted the exact TradeMux execution result into expected settlement evidence")
    settlement = settlement_evidence_payload(
        settlement_id=UUID("10000000-0000-4000-8000-000000000005"),
        evidence=expected[0],
        status="SETTLED",
        reconciled=True,
    )

    financial = load(
        repo("synergy_financial_os") / "contracts" / "accounting_recognition_v1.py",
        "financial_trading",
    )
    accounting = financial.accounting_recognition_payload(
        source_settlement_event_id=settlement["settlement_id"],
        recognition_id=UUID("10000000-0000-4000-8000-000000000006"),
        classification="ASSET_TRANSFER",
        entries=[
            {"account": "asset:broker", "side": "DEBIT", "asset": "USD", "amount": settlement["amount"]},
            {"account": "clearing:trades", "side": "CREDIT", "asset": "USD", "amount": settlement["amount"]},
        ],
        recognized_at=datetime(2026, 9, 28, 18, 2, tzinfo=timezone.utc),
        accounting_period="2026-09",
        hardnav_delta="0",
        settlement_payload=settlement,
    )
    witness("synergy_pay_system", "synergy_financial_os", "synergy.settlement.evidence/v1", "Financial OS recognized the exact reconciled Pay settlement payload")

    trust = dynamic_trust_commitment(accounting)
    witness("synergy_financial_os", "synergy_ai_blockchain", "synergy.accounting.recognition/v1", "Rust blockchain consumer committed the SHA-256 of the exact Financial OS accounting payload")
    SHARED["accounting"] = accounting
    SHARED["trust"] = trust


def science_path() -> None:
    nexus = load(repo("synergy_agi_nexus") / "contracts" / "ai_proposal_v1.py", "nexus_science")
    sci = load(repo("synergy_nexus_science_agent") / "contracts" / "science_contracts.py", "science_contract")
    mega = load(repo("synergy_megaproject") / "tools" / "science_contracts.py", "mega_science")
    proposal = nexus.ai_proposal_payload(
        proposal_id=UUID("11111111-1111-4111-8111-111111111111"),
        task_type="SCIENCE",
        model_id="nexus-v18:m3",
        proposal={"question": "Does deterministic M3 evidence binding reproduce?"},
        confidence=.61,
        limitations=["proposal only; independent evidence required"],
    )
    task = sci.science_task_from_nexus(proposal)
    assert task["authorization"] is False
    witness("synergy_agi_nexus", "synergy_nexus_science_agent", "synergy.ai.proposal/v1", "Science Agent accepted the exact NEXUS science proposal")
    src = sci.source_record(source_id="S-M3", locator="fixture:m3", content=b"measured fixture")
    package = sci.evidence_package_payload(
        research_question=proposal["proposal"]["question"],
        claims=[{"claim_id": "C-M3", "text": "fixture was measured", "epistemic_status": "MEASURED", "source_ids": ["S-M3"]}],
        sources=[src],
        status="REPRODUCED",
        reproduction_command="python m3_fixture.py",
    )
    queue = mega.science_package_to_review_queue(package)
    assert queue["canonical_graph_mutation"] is False
    witness("synergy_nexus_science_agent", "synergy_megaproject", "synergy.science.evidence-package/v1", "Megaproject consumed the exact Science Agent evidence package")


def engineering_path() -> None:
    sys.path.insert(0, str(repo("synergy_ai_language") / "src"))
    from ai_language.semantic_trace import build_semantic_trace
    from ai_language.synergy_contracts import requirement_trace_payload
    coder = load(repo("synergy_ai_coder") / "runtime" / "contracts.py", "coder_contract")
    meta = load(repo("synergy_meta_os") / "runtime" / "change_contracts.py", "meta_change")
    trace = build_semantic_trace("Implement typed boundary", ["runtime/contracts.py"])
    req = trace.requirements[0]
    trace.record("write_file", {"path": "runtime/contracts.py", "requirement_ids": [req.id]}, "OK: wrote")
    trace.record("run_command", {"command": "pytest", "requirement_ids": [req.id]}, "OK: pass")
    payload = requirement_trace_payload(trace, affected_repositories=["Shtenco/synergy_ai_coder"])[0]
    consumed = coder.consume_requirement_trace(payload, target_repository="Shtenco/synergy_ai_coder")
    assert consumed["requirement_id"] == req.id
    witness("synergy_ai_language", "synergy_ai_coder", "synergy.engineering.requirement-trace/v1", "AI Coder consumed the exact AI Language requirement trace")
    change = coder.change_evidence_payload(
        change_id=UUID("22222222-2222-4222-8222-222222222222"),
        repository="Shtenco/synergy_ai_coder",
        commit_sha="1" * 40,
        requirements=[req.id],
        checks=[coder.check_record(name="pytest", passed=True, evidence_bytes=b"PASS")],
        review_status="APPROVED",
        artifact_bytes=b"artifact",
    )
    meta.require_deployable_change(change, expected_repository="Shtenco/synergy_ai_coder")
    witness("synergy_ai_coder", "synergy_meta_os", "synergy.engineering.change-evidence/v1", "Meta-OS accepted the exact approved AI Coder change evidence")


def real_economy_path() -> None:
    nexus = load(repo("synergy_agi_nexus") / "contracts" / "ai_proposal_v1.py", "nexus_economy")
    e_ai = load(repo("synergy_eurasian") / "interfaces" / "ai_contracts.py", "eurasian_ai")
    e = load(repo("synergy_eurasian") / "interfaces" / "synergy_contracts.py", "eurasian_contract")
    gov = load(repo("synergy_project") / "contracts" / "capital_governance_v1.py", "capital_gov")
    sys.path.insert(0, str(repo("synergy_pay_system") / "src"))
    from synergy_pay.synergy_contracts import payment_intent_from_funding_authorization

    advisory_payload = nexus.ai_proposal_payload(
        proposal_id=UUID("30000000-0000-4000-8000-000000000001"),
        task_type="ECONOMY",
        model_id="nexus-v18:m3",
        proposal={"sector": "agro"},
        confidence=.60,
        limitations=["advisory only"],
    )
    advisory = e_ai.nexus_economy_advisory(advisory_payload)
    assert advisory["funding_authorization"] is False
    witness("synergy_agi_nexus", "synergy_eurasian", "synergy.ai.proposal/v1", "Eurasian consumed the exact NEXUS economy advisory without gaining funding authority")

    project = json.loads((repo("synergy_eurasian") / "examples" / "project_proposal_ai_agro.json").read_text(encoding="utf-8"))
    p = e.federation_project_proposal_payload(project)
    gov.validate_project_proposal(p)
    witness("synergy_eurasian", "synergy_project", "synergy.economy.project-proposal/v1", "Capital Governance validated the exact Eurasian project proposal")
    auth = gov.funding_authorization_payload(
        project_event_id=UUID("33333333-3333-4333-8333-333333333333"),
        authorization_id=UUID("44444444-4444-4444-8444-444444444444"),
        decision="AUTHORIZE",
        max_amount="100",
        currency="USD",
        authorized_rails=["bank"],
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        conditions=["M1"],
        approver_refs=["committee:1"],
        underwriting_evidence_ids=["evidence:m3"],
        policy_version="gov-m3",
    )
    intent = payment_intent_from_funding_authorization(
        auth, payer="treasury", payee="spv", amount="80"
    )
    assert intent.amount == Decimal("80")
    witness("synergy_project", "synergy_pay_system", "synergy.economy.funding-authorization/v1", "Pay built a bounded PaymentIntent from the exact Capital Governance authorization")


def runtime_network_path() -> None:
    compress = load(repo("synegy_ai_compress") / "compression_lab" / "synergy_contracts.py", "compress_contract")
    net = load(repo("synergy_net") / "runtime" / "synergy_contracts.py", "net_contract")
    sys.path.insert(0, str(repo("synergy_meta_os")))
    from runtime.transport_contracts import require_transport_delivery
    from runtime.archive_contracts import verify_archive_evidence
    from runtime.synergy_contracts import node_manifest_payload
    turbo = load(repo("synergy_turbo_linux") / "turbo_orchestrator" / "synergy_contracts.py", "turbo_contract")

    source = b"m3-content" * 32
    archive = b"archive-m3"
    ae = compress.archive_evidence_payload(source=source, archive=archive, restored=source, codec_id="m3-codec")

    content = net.consume_archive_evidence(ae)
    assert content["content_id"] == ae["source_sha256"]
    witness("synegy_ai_compress", "synergy_net", "synergy.archive.evidence/v1", "SynergyNet consumed the exact AI Compress archive evidence")

    with tempfile.TemporaryDirectory() as td:
        ap = Path(td) / "archive.bin"
        ap.write_bytes(archive)
        verify_archive_evidence(ae, ap)
    witness("synegy_ai_compress", "synergy_meta_os", "synergy.archive.evidence/v1", "Meta-OS verified the exact archive bytes against AI Compress evidence")

    te = net.transport_evidence_payload(
        session_id="m3",
        sender_peer="node-a",
        receiver_peer="node-b",
        content=archive,
        delivered_at=datetime.now(timezone.utc),
        transport_profile="authenticated-test",
        authenticated=True,
        route=["node-a", "node-b"],
        bytes_on_wire=len(archive) + 16,
        latency_ms=1.0,
    )
    require_transport_delivery(te)
    witness("synergy_net", "synergy_meta_os", "synergy.transport.evidence/v1", "Meta-OS accepted the exact authenticated SynergyNet transport evidence")

    blockchain = repo("synergy_ai_blockchain")
    out = subprocess.check_output([
        "cargo", "run", "--quiet", "--example", "federation_transport_consumer", "--",
        te["session_id"], te["sender_peer"], te["receiver_peer"], te["content_sha256"],
        "true" if te["authenticated"] else "false", ",".join(te["route"]),
        str(te["bytes_on_wire"]), str(te["latency_ms"]),
    ], cwd=blockchain, text=True)
    assert out.strip().startswith("PASS ")
    witness("synergy_net", "synergy_ai_blockchain", "synergy.transport.evidence/v1", "Rust blockchain consumer verified the exact SynergyNet transport evidence")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        artifact = root / "svc"
        artifact.write_bytes(b"svc")
        manifest = {
            "schema": 1,
            "node_id": "m3-node",
            "profile": "EDGE_CLIENT",
            "attested": False,
            "development": True,
            "generation": 1,
            "services": [{
                "name": "ui",
                "role": "EDGE_CLIENT",
                "artifact": "svc",
                "sha256": hashlib.sha256(b"svc").hexdigest(),
                "argv": ["$ARTIFACT"],
                "capabilities": ["storage.read", "ui.present"],
                "limits": {"memory_mib": 64, "cpu_seconds": 10, "open_files": 32},
            }],
        }
        mp = root / "manifest.json"
        mp.write_text(json.dumps(manifest), encoding="utf-8")
        node = node_manifest_payload(mp, root)
        host = turbo.consume_node_manifest(node)
        assert host["host_authority"] is False
    witness("synergy_meta_os", "synergy_turbo_linux", "synergy.runtime.node-manifest/v1", "TURBO consumed the exact verified Meta-OS node manifest")


def trust_ui_path() -> None:
    accounting = SHARED["accounting"]
    trust = SHARED["trust"]
    apps = load(repo("synergy_apps") / "runtime" / "read_models.py", "apps_contract")
    meta = load(repo("synergy_metachain") / "runtime" / "trust_contracts.py", "metachain_contract")

    view_accounting = apps.accounting_read_model(accounting)
    assert view_accounting["read_only"] is True
    witness("synergy_financial_os", "synergy_apps", "synergy.accounting.recognition/v1", "Apps rendered the exact Financial OS accounting artifact as a read-only projection")

    state = meta.CommitmentReplayState()
    claim = state.consume(trust)
    assert claim["claimable_once"] is True
    witness("synergy_ai_blockchain", "synergy_metachain", "synergy.trust.commitment/v1", "MetaChain consumed the exact FINALIZED blockchain trust commitment once")

    view_trust = apps.trust_read_model(trust)
    assert view_trust["read_only"] is True
    witness("synergy_ai_blockchain", "synergy_apps", "synergy.trust.commitment/v1", "Apps rendered the exact blockchain trust commitment as a read-only projection")


def main() -> int:
    check_lock()
    cases = [
        ("trading", trading_path),
        ("science", science_path),
        ("engineering", engineering_path),
        ("real-economy", real_economy_path),
        ("runtime-network", runtime_network_path),
        ("trust-ui", trust_ui_path),
    ]
    results = []
    all_pass = True
    for name, fn in cases:
        try:
            fn()
            print("PASS", name)
            results.append({"name": name, "status": "PASS", "error": None})
        except Exception as exc:
            all_pass = False
            print("FAIL", name, repr(exc))
            results.append({"name": name, "status": "FAIL", "error": repr(exc)})

    expected_edges = 22
    unique_edges = {
        (x["from"], x["to"], x["contract_id"]) for x in WITNESSES
    }
    edge_complete = len(WITNESSES) == expected_edges and len(unique_edges) == expected_edges
    if not edge_complete:
        all_pass = False
        print("FAIL edge-coverage", f"witnesses={len(WITNESSES)} unique={len(unique_edges)} expected={expected_edges}")

    lock_bytes = (HERE / "integration_lock_v1.json").read_bytes()
    evidence = {
        "schema": "synergy.m3-federation-evidence/v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lock_sha256": hashlib.sha256(lock_bytes).hexdigest(),
        "lock_repository_count": len(LOCK["repositories"]),
        "python": sys.version,
        "platform": platform.platform(),
        "results": results,
        "edge_witnesses": WITNESSES,
        "edge_witness_count": len(WITNESSES),
        "expected_edge_count": expected_edges,
        "all_pass": all_pass,
    }
    evidence_dir = HERE / "evidence"
    evidence_dir.mkdir(exist_ok=True)
    out = evidence_dir / "m3_federation_result.json"
    out.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")
    print("EVIDENCE", out)
    if not all_pass:
        return 1
    print("SYNERGY M3 FEDERATION EDGE-COMPLETE E2E: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
