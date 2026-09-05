from __future__ import annotations
import hashlib, json
from pathlib import Path

PARENT = "7de7c2dda23db2581294176bb262ae4aa8cbdc4ba97cdd4326278e88a9713a05"
EXPECTED_ADDITIONS = {"Shtenco/synergy_metachain","Shtenco/motherboard_xpu_xml","Shtenco/print_money_synergychain"}
SECRET_FAILURES = {"Shtenco/turbo_linux", "Shtenco/cashero", "Shtenco/usds"}
TOP = {"schema","candidate_id","as_of","owner","parent","repository_count","combined_repository_names","post_v2_additions","evidence_audit","policy","candidate_status","canonical_promotion","federation_candidate_digest"}
ADD = {"repository","origin","authority","classification","maturity","portfolio_cluster","role","next_milestone","top20_steps"}
AUDIT_TOP = {"schema","audit_id","as_of","owner","repository_count","parent_federation_v2_digest","audit_scope","audit_limitations","policy","records","audit_digest"}
AUDIT_REC = {"repository","profile","root","ci","tests","deps","secret_hygiene","canonical_drift"}

def _digest(obj: dict, key: str) -> str:
    x = dict(obj); x.pop(key, None)
    raw = json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()

def verify(candidate: dict, audit: dict) -> None:
    if set(candidate) != TOP: raise ValueError("candidate exact field set mismatch")
    if set(audit) != AUDIT_TOP: raise ValueError("audit exact field set mismatch")
    if candidate["schema"] != "synergy.repository-federation/v3-candidate": raise ValueError("schema")
    if audit["schema"] != "synergy.repository-evidence-audit/v1": raise ValueError("audit schema")
    if candidate["canonical_promotion"] is not False: raise ValueError("canonical promotion forbidden")
    if candidate["candidate_status"] != "AUDITED_SCOPE_EXPANSION_PENDING_HUMAN_REVIEW": raise ValueError("candidate status")
    if candidate["parent"] != {"schema":"synergy.repository-federation/v2","repository_count":42,"federation_digest":PARENT,"membership_inherited":True}: raise ValueError("parent federation")
    if audit["parent_federation_v2_digest"] != PARENT: raise ValueError("audit parent")
    if candidate["repository_count"] != 45 or audit["repository_count"] != 45: raise ValueError("repo count")
    names = candidate["combined_repository_names"]
    if len(names) != 45 or len(set(names)) != 45: raise ValueError("candidate membership")
    records = audit["records"]
    if len(records) != 45: raise ValueError("audit record count")
    for rec in records:
        if set(rec) != AUDIT_REC: raise ValueError("audit record exact field set mismatch")
    audit_names = [r["repository"] for r in records]
    if set(audit_names) != set(names) or len(set(audit_names)) != 45: raise ValueError("audit membership mismatch")
    additions = candidate["post_v2_additions"]
    if len(additions) != 3: raise ValueError("addition count")
    for item in additions:
        if set(item) != ADD: raise ValueError("addition exact field set mismatch")
        if item["origin"] != "DISCOVERED_AFTER_FEDERATION_V2": raise ValueError("addition origin")
        if not item["top20_steps"] or any(type(x) is not int or x < 1 or x > 20 for x in item["top20_steps"]): raise ValueError("invalid top20 step")
    if {x["repository"] for x in additions} != EXPECTED_ADDITIONS: raise ValueError("post-v2 additions")
    policy = candidate["policy"]
    if policy.get("auto_merge") is not False: raise ValueError("auto merge forbidden")
    if policy.get("merge_authority") != "HUMAN_MAINTAINER_ONLY": raise ValueError("merge authority")
    for key in ("ai_accounting_authority","ai_blockchain_submission_authority","ai_financial_authority","ai_payment_authority","ai_production_deployment_authority"):
        if policy.get(key) != "NONE": raise ValueError(f"authority escalation: {key}")
    if policy.get("internal_mint_or_revaluation_is_external_profit") is not False: raise ValueError("internal value cannot become external profit")
    failures = {r["repository"] for r in records if r["secret_hygiene"] == "EVIDENCED_FAIL_COMMITTED_SECRET_LIKE_FILE"}
    if not SECRET_FAILURES <= failures: raise ValueError("known security finding erased")
    if candidate["evidence_audit"] != {"audit_id":audit["audit_id"],"audit_digest":audit["audit_digest"]}: raise ValueError("audit binding")
    if audit["audit_digest"] != _digest(audit, "audit_digest"): raise ValueError("audit digest")
    if candidate["federation_candidate_digest"] != _digest(candidate, "federation_candidate_digest"): raise ValueError("candidate digest")

def main() -> int:
    root = Path(__file__).resolve().parents[1]
    candidate = json.loads((root/"registry/repository_federation_v3_candidate_20260905.json").read_text())
    audit = json.loads((root/"registry/repository_evidence_audit_v1_20260905.json").read_text())
    verify(candidate, audit)
    print("Repository Federation v3 candidate: VERIFIED (non-canonical candidate)")
    return 0

if __name__ == "__main__": raise SystemExit(main())
