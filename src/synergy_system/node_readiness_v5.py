from __future__ import annotations

import hashlib
import json
from typing import Any

class NodeReadinessV5Error(ValueError):
    pass

PROFILE="406740705e853fa51ad4eacf7a01925fbe4b5cec491be35ea12ba777d217d714"
BASE_LOCK="14c763218602585d49e12060e1e6cf21d33815fda0cb18711a6522a26157ace2"
REVISION="82d4b40e2276b8095f7fd3ff2105181d9c038b3e2879265facd022ff30d9fb32"
TOOLCHAIN="af92c9f1909ae3b64aaea78bdce2c6d05deb974ad242482b36e0c8ce820a2848"
BUILDER="5fe5d1e8b8e12d1c6408590e93d3e5abe1a208d921ae20066c45a813e036eaed"
NEG="564dfab1230dc28270dfc392125234208e4762400a6488c5d53a936f3d9bbdaa"
ASET="bc7d89378424a18727b90072c86e06238ea14e64bfb9dfc4464f184297eddf84"
PLAN="74c32607bc9fdadf43dddc87c58aa58adeaa2d795553d02cba87cf55ca12ec98"
PREV_READY="ee20353d76d377f31f8054dae0c6463db4b3aae1a57b4ccfc2d7631e2251a95b"
READY="01c706352c6a63d8545373b29999dba9a9d3407bcf5c5e804e3e82a2571e2112"

NEXUS={"artifact":"e87d00809ff976c76655b892166ec1cf1f13a893927ead156295b6814fcd9325","size":56965,"input":"8aa909ec32879b406fc0da03b27e10283c1970d1b06b3ed35da8f9b25191a274","recipe":"15bed077a6722b5fc074cf94ccf23de91540fff5301cb30a9eddc8ef2f0cd05f","evidence":"1e3c566388a7beb0552acad285b19d7a934bb92c9b08af112f30d73d979df864","runtime":"e7e9bfd5684e8a1c3b0964288945d750d8cc109869a5dae54fc3ad64de5e8998","location":"65945f7cce45b6e7da40a59121b84013483da13f61027a1c93a8dc37fc659568","file":"1yyCOrePdOoYFybGZoDGA5jcNdQdiHPpy","manifest":"f91ff32f64e83331b9989d1f89f80d870f9f1ee2aa212292d9b6f6d12f4bd25e"}
NET={"artifact":"7f22e68d80a7df879af71ebccdb45f8edb10cae3698bf07faa7076ce76fd0ef7","size":12837,"recipe":"37cb503fb8c6d5e8ef2305ce03d0332abee2d9eed5bb29f90364e20874d128df","evidence":"8c4f44f1b0b95221d660bb4a7c0598ada17e86f59bade16e85d93789bf1ddd8c","location":"de7d250414701a1b5a4e9fb31b8853d17882345829804121c569955075224fad","file":"1zuB8rjKO0HHIZmvUEGZnAbnkKGNN59qp","manifest":"fde462820a5d8a1b8c48c565a1ccd5fa3a72a9f36a2deec5305af3ce021d4de6","content_runtime":"abb35edd0336ea36f249d24b04e1b7482fea4ecebc5c881b655bf8a390d8b5ad","relay_runtime":"8c38cd130e3dd73723e3a3241d2df61bef218abdab2d16785ccec5b172fac4df"}

def canonical(v:Any)->bytes:
    return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()

def digest(v:dict[str,Any],field:str)->str:
    b=dict(v); b.pop(field,None)
    return hashlib.sha256(canonical(b)).hexdigest()

def require_self(v,field,expected):
    if v.get(field)!=expected or digest(v,field)!=expected:
        raise NodeReadinessV5Error(f"{field} mismatch")

def verify_negative(v):
    require_self(v,"evidence_digest",NEG)
    if v.get("schema")!="synergy.central-self-digest-negative-evidence/v1": raise NodeReadinessV5Error("negative evidence schema")
    a=v.get("artifact_set_v2",{}); p=v.get("build_plan_v5",{})
    if (a.get("claimed_self_digest"),a.get("canonical_recomputed_self_digest"))!=("43eb975763032f576cad87dff4d71fd520eae538a51940fccf335b522a88b51e","8a9617369ce5b60f9b86da866300053f6cdb24f9f90322877e9a5e0a24300f3b"): raise NodeReadinessV5Error("artifact-set negative evidence drift")
    if (p.get("claimed_self_digest"),p.get("canonical_recomputed_self_digest"))!=("6456618c98dc5df9d2843128db7787e6e0551003567ea282aaa015997b17b667","97266c83362027530feaeec9d84791be4029a9963948b17379b53b6e5f982567"): raise NodeReadinessV5Error("build-plan negative evidence drift")
    if v.get("effect")!="DO_NOT_USE_V2_OR_V5_AS_CANONICAL_ROOT" or v.get("execution_authority")!="NONE": raise NodeReadinessV5Error("negative evidence effect drift")

def verify_location(location,exp,repo,runtime_required=None):
    if location.get("schema")!="synergy.artifact-location-evidence/v1" or location.get("repository")!=repo: raise NodeReadinessV5Error("location identity drift")
    if (location.get("artifact_digest"),location.get("artifact_size"),location.get("artifact_manifest_digest"))!=(exp["artifact"],exp["size"],exp["manifest"]): raise NodeReadinessV5Error("location artifact drift")
    if location.get("build_recipe_digest")!=exp["recipe"] or location.get("build_evidence_digest")!=exp["evidence"]: raise NodeReadinessV5Error("location build binding drift")
    if runtime_required and location.get("runtime_spec_digest")!=runtime_required: raise NodeReadinessV5Error("location runtime binding drift")
    if location.get("provider")!="GOOGLE_DRIVE_CONNECTED_FILE" or location.get("provider_file_id")!=exp["file"]: raise NodeReadinessV5Error("location provider drift")
    pre=location.get("pre_upload_validation",{})
    if (pre.get("sha256"),pre.get("size"),pre.get("status"))!=(exp["artifact"],exp["size"],"PASS"): raise NodeReadinessV5Error("location pre-upload validation drift")
    if location.get("availability_status")!="DURABLE_CONNECTED_DRIVE_BINARY" or location.get("resolution_contract")!="FETCH_BY_PROVIDER_FILE_ID_THEN_VERIFY_SHA256_AND_SIZE_BEFORE_EXECUTION" or location.get("execution_authority")!="NONE": raise NodeReadinessV5Error("location availability/authority drift")

def verify_nexus(build_input,recipe,evidence,runtime,location):
    require_self(build_input,"build_input_digest",NEXUS["input"]); require_self(recipe,"recipe_digest",NEXUS["recipe"]); require_self(evidence,"evidence_digest",NEXUS["evidence"]); require_self(runtime,"runtime_spec_digest",NEXUS["runtime"]); require_self(location,"location_evidence_digest",NEXUS["location"])
    if build_input.get("schema")!="synergy.deterministic-zipapp-build-input/v2" or build_input.get("repository")!="Shtenco/agi_nexus": raise NodeReadinessV5Error("nexus input identity")
    if (build_input.get("expected_artifact_digest"),build_input.get("expected_artifact_size"),build_input.get("expected_manifest_digest"))!=(NEXUS["artifact"],NEXUS["size"],NEXUS["manifest"]): raise NodeReadinessV5Error("nexus input output drift")
    if recipe.get("schema")!="synergy.build-recipe/v4" or recipe.get("build_input_digest")!=NEXUS["input"] or recipe.get("artifact_digest")!=NEXUS["artifact"] or recipe.get("artifact_size")!=NEXUS["size"]: raise NodeReadinessV5Error("nexus recipe drift")
    if recipe.get("toolchain_lock_digest")!=TOOLCHAIN or recipe.get("builder_sha256")!=BUILDER or recipe.get("reproducibility_status")!="REPRODUCIBLE_BYTE_IDENTICAL": raise NodeReadinessV5Error("nexus toolchain/reproducibility drift")
    builds=evidence.get("builds")
    if evidence.get("schema")!="synergy.build-evidence/v2" or evidence.get("recipe_digest")!=NEXUS["recipe"] or evidence.get("build_input_digest")!=NEXUS["input"] or evidence.get("byte_identical") is not True or evidence.get("build_count")!=2 or not isinstance(builds,list) or len(builds)!=2: raise NodeReadinessV5Error("nexus build evidence drift")
    if any((b.get("artifact_digest"),b.get("artifact_size"))!=(NEXUS["artifact"],NEXUS["size"]) for b in builds): raise NodeReadinessV5Error("nexus build output drift")
    tests=evidence.get("executed_smoke_tests",[])
    if len(tests)<2 or any(t.get("status")!="PASS" for t in tests): raise NodeReadinessV5Error("nexus smoke evidence drift")
    if runtime.get("schema")!="synergy.artifact-runtime-spec/v2" or runtime.get("artifact_digest")!=NEXUS["artifact"]: raise NodeReadinessV5Error("nexus runtime drift")
    for f in ("network_access","process_execution_authority","financial_authority","execution_authority","remote_filesystem_path_authority"):
        if runtime.get(f)!="NONE": raise NodeReadinessV5Error(f"nexus {f} escalation")
    verify_location(location,NEXUS,"Shtenco/agi_nexus",runtime_required=NEXUS["runtime"])

def verify_synergynet(recipe,evidence,content_runtime,relay_runtime,location):
    require_self(recipe,"recipe_digest",NET["recipe"]); require_self(evidence,"evidence_digest",NET["evidence"]); require_self(content_runtime,"runtime_spec_digest",NET["content_runtime"]); require_self(relay_runtime,"runtime_spec_digest",NET["relay_runtime"]); require_self(location,"location_evidence_digest",NET["location"])
    if recipe.get("schema")!="synergy.build-recipe/v3" or recipe.get("repository")!="Shtenco/synergynet" or recipe.get("artifact_digest")!=NET["artifact"] or recipe.get("artifact_size")!=NET["size"]: raise NodeReadinessV5Error("synergynet recipe drift")
    if recipe.get("toolchain_lock_digest")!=TOOLCHAIN or recipe.get("builder_sha256")!=BUILDER or recipe.get("reproducibility_status")!="REPRODUCIBLE_BYTE_IDENTICAL": raise NodeReadinessV5Error("synergynet toolchain/reproducibility drift")
    builds=evidence.get("builds")
    if evidence.get("schema")!="synergy.build-evidence/v1" or evidence.get("recipe_digest")!=NET["recipe"] or evidence.get("byte_identical") is not True or evidence.get("build_count")!=2 or not isinstance(builds,list) or len(builds)!=2: raise NodeReadinessV5Error("synergynet evidence drift")
    if any((b.get("artifact_digest"),b.get("artifact_size"))!=(NET["artifact"],NET["size"]) for b in builds): raise NodeReadinessV5Error("synergynet build output drift")
    tests=evidence.get("executed_smoke_tests",[])
    if not tests or any(t.get("status")!="PASS" for t in tests): raise NodeReadinessV5Error("synergynet smoke drift")
    for spec,sid,expected in ((content_runtime,"content-cache",NET["content_runtime"]),(relay_runtime,"synergynet",NET["relay_runtime"])):
        if spec.get("schema")!="synergy.artifact-runtime-spec/v1" or spec.get("service_id")!=sid or spec.get("artifact_digest")!=NET["artifact"] or spec.get("runtime_spec_digest")!=expected or spec.get("execution_authority")!="NONE" or spec.get("remote_filesystem_path_authority")!="NONE": raise NodeReadinessV5Error(f"{sid} runtime drift")
    verify_location(location,NET,"Shtenco/synergynet")

def expected_services():
    common={"repository":"Shtenco/synergynet","artifact_digest":NET["artifact"],"artifact_size":NET["size"],"build_recipe_digest":NET["recipe"],"build_evidence_digest":NET["evidence"],"artifact_location_evidence_digest":NET["location"],"provider":"GOOGLE_DRIVE_CONNECTED_FILE","provider_file_id":NET["file"],"artifact_status":"VERIFIED_EXECUTABLE","reproducibility_status":"REPRODUCIBLE_BYTE_IDENTICAL","availability_status":"DURABLE_CONNECTED_DRIVE_BINARY","resolution_contract":"FETCH_BY_PROVIDER_FILE_ID_THEN_VERIFY_SHA256_AND_SIZE_BEFORE_EXECUTION","execution_authority":"NONE"}
    c={"service_id":"content-cache",**common,"artifact_runtime_spec_digest":NET["content_runtime"]}; r={"service_id":"synergynet",**common,"artifact_runtime_spec_digest":NET["relay_runtime"]}
    n={"service_id":"nexus","repository":"Shtenco/agi_nexus","artifact_digest":NEXUS["artifact"],"artifact_size":NEXUS["size"],"build_recipe_digest":NEXUS["recipe"],"build_evidence_digest":NEXUS["evidence"],"artifact_runtime_spec_digest":NEXUS["runtime"],"artifact_location_evidence_digest":NEXUS["location"],"provider":"GOOGLE_DRIVE_CONNECTED_FILE","provider_file_id":NEXUS["file"],"artifact_status":"VERIFIED_EXECUTABLE","reproducibility_status":"REPRODUCIBLE_BYTE_IDENTICAL","availability_status":"DURABLE_CONNECTED_DRIVE_BINARY","resolution_contract":"FETCH_BY_PROVIDER_FILE_ID_THEN_VERIFY_SHA256_AND_SIZE_BEFORE_EXECUTION","network_access":"NONE","process_execution_authority":"NONE","financial_authority":"NONE","execution_authority":"NONE","historical_artifact_digest":"fa7bbd141566d1542a5c03ee485de8ebd5f2ed76557ac56ff728196429fbbb64","lineage_transition":"V1_HISTORICAL_TO_V2_CURRENT_PRESERVE_HISTORY"}
    return [c,n,r]

def verify_artifact_set_v3(aset,negative):
    verify_negative(negative); require_self(aset,"artifact_set_digest",ASET)
    if aset.get("schema")!="synergy.node-artifact-set/v3" or aset.get("central_self_digest_negative_evidence_digest")!=NEG or aset.get("toolchain_lock_digest")!=TOOLCHAIN: raise NodeReadinessV5Error("artifact set root drift")
    if aset.get("previous_artifact_set_claimed_digest")!="43eb975763032f576cad87dff4d71fd520eae538a51940fccf335b522a88b51e" or aset.get("previous_artifact_set_canonical_digest")!="8a9617369ce5b60f9b86da866300053f6cdb24f9f90322877e9a5e0a24300f3b": raise NodeReadinessV5Error("artifact set ancestry drift")
    if aset.get("services")!=expected_services(): raise NodeReadinessV5Error("artifact set service bindings drift")
    if aset.get("artifact_set_status")!="ALL_ARTIFACTS_VERIFIED_AND_DURABLY_LOCATABLE" or aset.get("execution_authority")!="NONE": raise NodeReadinessV5Error("artifact set status/authority drift")
    return aset

def verify_build_plan_v6(plan,aset,negative):
    verify_artifact_set_v3(aset,negative); require_self(plan,"plan_digest",PLAN)
    if plan.get("schema")!="synergy.node-build-plan/v6" or plan.get("artifact_set_digest")!=ASET or plan.get("central_self_digest_negative_evidence_digest")!=NEG: raise NodeReadinessV5Error("plan root drift")
    for f,e in (("profile_digest",PROFILE),("base_source_lock_digest",BASE_LOCK),("source_revision_digest",REVISION),("toolchain_lock_digest",TOOLCHAIN)):
        if plan.get(f)!=e: raise NodeReadinessV5Error(f"plan {f} drift")
    if plan.get("previous_build_plan_claimed_digest")!="6456618c98dc5df9d2843128db7787e6e0551003567ea282aaa015997b17b667" or plan.get("previous_build_plan_canonical_digest")!="97266c83362027530feaeec9d84791be4029a9963948b17379b53b6e5f982567": raise NodeReadinessV5Error("plan corrected ancestry drift")
    if plan.get("services")!=aset.get("services") or plan.get("build_blockers")!=[]: raise NodeReadinessV5Error("plan services/blockers drift")
    if plan.get("plan_status")!="BUILD_ARTIFACTS_VERIFIED_REPRODUCIBLE_DURABLY_LOCATABLE" or plan.get("execution_authority")!="NONE": raise NodeReadinessV5Error("plan status/authority drift")
    return plan

def verify_readiness_v5(readiness,plan,aset,negative,build_input,nexus_recipe,nexus_evidence,nexus_runtime,nexus_location,net_recipe,net_evidence,content_runtime,relay_runtime,net_location):
    verify_nexus(build_input,nexus_recipe,nexus_evidence,nexus_runtime,nexus_location); verify_synergynet(net_recipe,net_evidence,content_runtime,relay_runtime,net_location); verify_build_plan_v6(plan,aset,negative); require_self(readiness,"readiness_digest",READY)
    if readiness.get("schema")!="synergy.node-readiness/v5" or readiness.get("previous_readiness_digest")!=PREV_READY: raise NodeReadinessV5Error("readiness ancestry drift")
    for f,e in (("profile_digest",PROFILE),("base_source_lock_digest",BASE_LOCK),("source_revision_digest",REVISION),("build_plan_digest",PLAN),("toolchain_lock_digest",TOOLCHAIN),("artifact_set_digest",ASET),("central_self_digest_negative_evidence_digest",NEG)):
        if readiness.get(f)!=e: raise NodeReadinessV5Error(f"readiness {f} drift")
    if readiness.get("blockers")!=[] or readiness.get("node_status")!="NODE_ADMISSION_READY_NOT_RUNNING" or readiness.get("auto_start") is not False: raise NodeReadinessV5Error("readiness state drift")
    if readiness.get("build_status")!="BUILD_ARTIFACTS_VERIFIED_REPRODUCIBLE_DURABLY_LOCATABLE" or readiness.get("service_status")!="ALL_REQUIRED_SERVICES_ARTIFACT_VERIFIED_AND_DURABLY_LOCATABLE": raise NodeReadinessV5Error("readiness evidence status drift")
    for f in ("financial_authority","payment_authority","accounting_authority","execution_authority"):
        if readiness.get(f)!="NONE": raise NodeReadinessV5Error(f"readiness {f} escalation")
    return readiness
