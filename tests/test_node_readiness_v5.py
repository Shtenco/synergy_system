from __future__ import annotations

import copy
import json
from pathlib import Path
import pytest

from synergy_system.node_readiness_v5 import NodeReadinessV5Error, digest, verify_artifact_set_v3, verify_readiness_v5

ROOT=Path(__file__).resolve().parents[1]
def load(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))

def bundle():
    return {
        "readiness":load("fixtures/node_readiness/research_compute_node_readiness_v5.json"),
        "plan":load("fixtures/node_build_plans/research_compute_node_build_plan_durable_v6.json"),
        "aset":load("fixtures/artifact_sets/research_compute_node_artifact_set_v3.json"),
        "negative":load("evidence/research_compute_node_self_digest_negative_evidence_v1.json"),
        "build_input":load("fixtures/build_inputs/agi_nexus_artifact_build_input_v2.json"),
        "nexus_recipe":load("fixtures/build_recipes/agi_nexus_build_recipe_v4.json"),
        "nexus_evidence":load("fixtures/build_evidence/agi_nexus_build_evidence_v2.json"),
        "nexus_runtime":load("fixtures/artifact_runtime_specs/agi_nexus_artifact_runtime_spec_v2.json"),
        "nexus_location":load("fixtures/artifact_location_evidence/agi_nexus_artifact_location_evidence_v1.json"),
        "net_recipe":load("fixtures/build_recipes/synergynet_build_recipe_v3.json"),
        "net_evidence":load("fixtures/build_evidence/synergynet_build_evidence_v1.json"),
        "content_runtime":load("fixtures/artifact_runtime_specs/synergynet_content_cache_artifact_runtime_spec_v1.json"),
        "relay_runtime":load("fixtures/artifact_runtime_specs/synergynet_relay_artifact_runtime_spec_v1.json"),
        "net_location":load("fixtures/artifact_location_evidence/synergynet_artifact_location_evidence_v1.json"),
    }

def verify(b):
    return verify_readiness_v5(b["readiness"],b["plan"],b["aset"],b["negative"],b["build_input"],b["nexus_recipe"],b["nexus_evidence"],b["nexus_runtime"],b["nexus_location"],b["net_recipe"],b["net_evidence"],b["content_runtime"],b["relay_runtime"],b["net_location"])

def test_v5_historical_bundle_is_rejected_after_location_self_digest_audit():
    b=bundle()
    # v5 bound the historical claimed location root 65945f..., but a later
    # canonical audit proved that the v1 bytes rehash to b5fbec38.... v6 is
    # the additive corrected successor and is the generation allowed to pass.
    assert b["nexus_location"]["location_evidence_digest"] == "65945f7cce45b6e7da40a59121b84013483da13f61027a1c93a8dc37fc659568"
    assert digest(b["nexus_location"],"location_evidence_digest") == "b5fbec38847392e9986cb6cc02b83d87247bba2425e5b50b7c598e203ab1ed33"
    with pytest.raises(NodeReadinessV5Error, match="location_evidence_digest mismatch"):
        verify(b)

def test_old_self_digest_invalid_artifact_set_is_not_v3_root():
    b=bundle(); old=load("fixtures/artifact_sets/research_compute_node_artifact_set_v2.json")
    with pytest.raises(NodeReadinessV5Error): verify_artifact_set_v3(old,b["negative"])

def test_fresh_hash_cannot_substitute_drive_file_id():
    b=bundle(); x=copy.deepcopy(b["nexus_location"]); x["provider_file_id"]="attacker-file"; x["location_evidence_digest"]=digest(x,"location_evidence_digest"); b["nexus_location"]=x
    with pytest.raises(NodeReadinessV5Error): verify(b)

def test_fresh_hash_cannot_fake_preupload_size():
    b=bundle(); x=copy.deepcopy(b["net_location"]); x["pre_upload_validation"]["size"]=12836; x["location_evidence_digest"]=digest(x,"location_evidence_digest"); b["net_location"]=x
    with pytest.raises(NodeReadinessV5Error): verify(b)

def test_historical_nexus_artifact_cannot_be_repromoted():
    b=bundle(); a=copy.deepcopy(b["aset"]); a["services"][1]["artifact_digest"]="fa7bbd141566d1542a5c03ee485de8ebd5f2ed76557ac56ff728196429fbbb64"; a["artifact_set_digest"]=digest(a,"artifact_set_digest"); b["aset"]=a
    with pytest.raises(NodeReadinessV5Error): verify(b)

def test_negative_evidence_cannot_be_erased_with_fresh_hashes():
    b=bundle(); a=copy.deepcopy(b["aset"]); a["central_self_digest_negative_evidence_digest"]="0"*64; a["artifact_set_digest"]=digest(a,"artifact_set_digest"); b["aset"]=a
    with pytest.raises(NodeReadinessV5Error): verify(b)

def test_nexus_cannot_gain_financial_or_network_authority():
    b=bundle(); r=copy.deepcopy(b["nexus_runtime"]); r["network_access"]="ARBITRARY"; r["financial_authority"]="TREASURY"; r["runtime_spec_digest"]=digest(r,"runtime_spec_digest"); b["nexus_runtime"]=r
    with pytest.raises(NodeReadinessV5Error): verify(b)

def test_readiness_cannot_autostart_or_gain_accounting_authority():
    b=bundle(); r=copy.deepcopy(b["readiness"]); r["auto_start"]=True; r["accounting_authority"]="FINANCIAL_OS"; r["readiness_digest"]=digest(r,"readiness_digest"); b["readiness"]=r
    with pytest.raises(NodeReadinessV5Error): verify(b)

def test_plan_cannot_erase_evidence_and_keep_empty_blockers():
    b=bundle(); p=copy.deepcopy(b["plan"]); p["services"][1]["artifact_location_evidence_digest"]="0"*64; p["plan_digest"]=digest(p,"plan_digest"); b["plan"]=p
    with pytest.raises(NodeReadinessV5Error): verify(b)
