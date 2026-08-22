from __future__ import annotations
import copy,json
from pathlib import Path
import pytest
from synergy_system.node_readiness_v6 import NodeReadinessV6Error,digest,verify_readiness_v6

ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
def bundle():
    return {"readiness":load("fixtures/node_readiness/research_compute_node_readiness_v6.json"),"plan":load("fixtures/node_build_plans/research_compute_node_build_plan_durable_v7.json"),"aset":load("fixtures/artifact_sets/research_compute_node_artifact_set_v4.json"),"central_negative":load("evidence/research_compute_node_self_digest_negative_evidence_v1.json"),"location_negative":load("evidence/research_compute_node_location_evidence_self_digest_negative_evidence_v1.json"),"build_input":load("fixtures/build_inputs/agi_nexus_artifact_build_input_v2.json"),"nexus_recipe":load("fixtures/build_recipes/agi_nexus_build_recipe_v4.json"),"nexus_evidence":load("fixtures/build_evidence/agi_nexus_build_evidence_v2.json"),"nexus_runtime":load("fixtures/artifact_runtime_specs/agi_nexus_artifact_runtime_spec_v2.json"),"nexus_location":load("fixtures/artifact_location_evidence/agi_nexus_artifact_location_evidence_v2.json"),"net_recipe":load("fixtures/build_recipes/synergynet_build_recipe_v3.json"),"net_evidence":load("fixtures/build_evidence/synergynet_build_evidence_v1.json"),"content_runtime":load("fixtures/artifact_runtime_specs/synergynet_content_cache_artifact_runtime_spec_v1.json"),"relay_runtime":load("fixtures/artifact_runtime_specs/synergynet_relay_artifact_runtime_spec_v1.json"),"net_location":load("fixtures/artifact_location_evidence/synergynet_artifact_location_evidence_v2.json")}
def verify(b): return verify_readiness_v6(b["readiness"],b["plan"],b["aset"],b["central_negative"],b["location_negative"],b["build_input"],b["nexus_recipe"],b["nexus_evidence"],b["nexus_runtime"],b["nexus_location"],b["net_recipe"],b["net_evidence"],b["content_runtime"],b["relay_runtime"],b["net_location"])

def test_canonical_v6_passes_fail_closed():
    out=verify(bundle()); assert out["blockers"]==[] and out["node_status"]=="NODE_ADMISSION_READY_NOT_RUNNING" and out["auto_start"] is False
    assert all(out[x]=="NONE" for x in ("financial_authority","payment_authority","accounting_authority","execution_authority"))

def test_v1_nexus_location_claim_cannot_be_repromoted():
    b=bundle(); x=copy.deepcopy(b["nexus_location"]); x["schema"]="synergy.artifact-location-evidence/v1"; x["location_evidence_digest"]="65945f7cce45b6e7da40a59121b84013483da13f61027a1c93a8dc37fc659568"; b["nexus_location"]=x
    with pytest.raises(NodeReadinessV6Error): verify(b)

def test_v1_synergynet_location_canonical_rehash_cannot_be_repromoted():
    b=bundle(); x=copy.deepcopy(b["net_location"]); x["schema"]="synergy.artifact-location-evidence/v1"; x["location_evidence_digest"]="e99328bf818c774628ea5f2db597ac2250ad2068e5192f04c3bc96f39417ea55"; b["net_location"]=x
    with pytest.raises(NodeReadinessV6Error): verify(b)

def test_location_negative_evidence_cannot_be_erased():
    b=bundle(); a=copy.deepcopy(b["aset"]); a["location_evidence_self_digest_negative_evidence_digest"]="0"*64; a["artifact_set_digest"]=digest(a,"artifact_set_digest"); b["aset"]=a
    with pytest.raises(NodeReadinessV6Error): verify(b)

def test_drive_file_substitution_rejected_even_with_fresh_location_hash():
    b=bundle(); x=copy.deepcopy(b["nexus_location"]); x["provider_file_id"]="fake"; x["location_evidence_digest"]=digest(x,"location_evidence_digest"); b["nexus_location"]=x
    with pytest.raises(NodeReadinessV6Error): verify(b)

def test_artifact_sha_substitution_rejected_even_with_fresh_outer_hashes():
    b=bundle(); x=copy.deepcopy(b["nexus_location"]); x["artifact_digest"]="0"*64; x["pre_upload_validation"]["sha256"]="0"*64; x["location_evidence_digest"]=digest(x,"location_evidence_digest"); b["nexus_location"]=x
    with pytest.raises(NodeReadinessV6Error): verify(b)

def test_nexus_cannot_gain_network_process_or_financial_authority():
    b=bundle(); x=copy.deepcopy(b["nexus_runtime"]); x["network_access"]="ARBITRARY"; x["process_execution_authority"]="SPAWN"; x["financial_authority"]="TREASURY"; x["runtime_spec_digest"]=digest(x,"runtime_spec_digest"); b["nexus_runtime"]=x
    with pytest.raises(NodeReadinessV6Error): verify(b)

def test_readiness_cannot_start_or_gain_payment_accounting_authority():
    b=bundle(); x=copy.deepcopy(b["readiness"]); x["auto_start"]=True; x["payment_authority"]="METAPAY"; x["accounting_authority"]="FINANCIAL_OS"; x["readiness_digest"]=digest(x,"readiness_digest"); b["readiness"]=x
    with pytest.raises(NodeReadinessV6Error): verify(b)

def test_plan_cannot_erase_blocker_derivation_bindings():
    b=bundle(); x=copy.deepcopy(b["plan"]); x["services"][1]["artifact_location_evidence_digest"]="0"*64; x["plan_digest"]=digest(x,"plan_digest"); b["plan"]=x
    with pytest.raises(NodeReadinessV6Error): verify(b)
