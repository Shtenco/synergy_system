from __future__ import annotations
import hashlib,json
from typing import Any

class NodeReadinessV6Error(ValueError): pass

PROFILE="406740705e853fa51ad4eacf7a01925fbe4b5cec491be35ea12ba777d217d714"
BASE="14c763218602585d49e12060e1e6cf21d33815fda0cb18711a6522a26157ace2"
REV="82d4b40e2276b8095f7fd3ff2105181d9c038b3e2879265facd022ff30d9fb32"
TOOL="af92c9f1909ae3b64aaea78bdce2c6d05deb974ad242482b36e0c8ce820a2848"
BUILDER="5fe5d1e8b8e12d1c6408590e93d3e5abe1a208d921ae20066c45a813e036eaed"
CENTRAL_NEG="564dfab1230dc28270dfc392125234208e4762400a6488c5d53a936f3d9bbdaa"
LOCATION_NEG="f17fdeab2dceb1aca3d939b57a6d5374eba6988c5f7b991ad80d3e9523d4e107"
ASET="d479b71a0756288b5d8d6d7d7433881cbd448a63c22bc9f87f271df7f82479c2"
PLAN="46a4ee4c01fba5fb8c5e3cff51b4f6b5e7090347ef1ec1ab6763a606a31aaa2e"
READY="6714beff9f366ed19c6b000b9239afffcd797cfc9d3fc4319b70a8af53b9af1f"
N_ART="e87d00809ff976c76655b892166ec1cf1f13a893927ead156295b6814fcd9325"
N_SIZE=56965
N_MAN="f91ff32f64e83331b9989d1f89f80d870f9f1ee2aa212292d9b6f6d12f4bd25e"
N_INPUT="8aa909ec32879b406fc0da03b27e10283c1970d1b06b3ed35da8f9b25191a274"
N_RECIPE="15bed077a6722b5fc074cf94ccf23de91540fff5301cb30a9eddc8ef2f0cd05f"
N_EVID="1e3c566388a7beb0552acad285b19d7a934bb92c9b08af112f30d73d979df864"
N_RUNTIME="e7e9bfd5684e8a1c3b0964288945d750d8cc109869a5dae54fc3ad64de5e8998"
N_LOC="341989039238b9735018bad71c2ac1f0114ae15b4736faa524b5f7a643c27f47"
N_FILE="1yyCOrePdOoYFybGZoDGA5jcNdQdiHPpy"
S_ART="7f22e68d80a7df879af71ebccdb45f8edb10cae3698bf07faa7076ce76fd0ef7"
S_SIZE=12837
S_MAN="fde462820a5d8a1b8c48c565a1ccd5fa3a72a9f36a2deec5305af3ce021d4de6"
S_RECIPE="37cb503fb8c6d5e8ef2305ce03d0332abee2d9eed5bb29f90364e20874d128df"
S_EVID="8c4f44f1b0b95221d660bb4a7c0598ada17e86f59bade16e85d93789bf1ddd8c"
C_RUNTIME="abb35edd0336ea36f249d24b04e1b7482fea4ecebc5c881b655bf8a390d8b5ad"
R_RUNTIME="8c38cd130e3dd73723e3a3241d2df61bef218abdab2d16785ccec5b172fac4df"
S_LOC="c4102a8e668b79fc961a5f1767154154f4a600d320442770d74c7a006a5cee08"
S_FILE="1zuB8rjKO0HHIZmvUEGZnAbnkKGNN59qp"

def canonical(v:Any)->bytes: return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
def digest(v:dict[str,Any],field:str)->str:
    b=dict(v);b.pop(field,None);return hashlib.sha256(canonical(b)).hexdigest()
def req(c:bool,m:str):
    if not c: raise NodeReadinessV6Error(m)
def selfhash(v,field,expected): req(v.get(field)==expected and digest(v,field)==expected,f"{field} mismatch")

def verify_negatives(central,location):
    selfhash(central,"evidence_digest",CENTRAL_NEG)
    req(central.get("effect")=="DO_NOT_USE_V2_OR_V5_AS_CANONICAL_ROOT" and central.get("execution_authority")=="NONE","central negative evidence drift")
    selfhash(location,"evidence_digest",LOCATION_NEG)
    req(location.get("effect")=="DO_NOT_USE_V1_LOCATION_EVIDENCE_OR_DEPENDENT_ROOTS_AS_CANONICAL" and location.get("correction_policy")=="ADDITIVE_NEW_GENERATIONS_ONLY" and location.get("execution_authority")=="NONE","location negative evidence drift")
    n=location.get("nexus_location_evidence_v1",{});s=location.get("synergynet_location_evidence_v1",{})
    req((n.get("claimed_self_digest"),n.get("canonical_recomputed_self_digest"),n.get("corrected_v2_digest"))==("65945f7cce45b6e7da40a59121b84013483da13f61027a1c93a8dc37fc659568","b5fbec38847392e9986cb6cc02b83d87247bba2425e5b50b7c598e203ab1ed33",N_LOC),"NEXUS location correction drift")
    req((s.get("claimed_self_digest"),s.get("canonical_recomputed_self_digest"),s.get("corrected_v2_digest"))==("de7d250414701a1b5a4e9fb31b8853d17882345829804121c569955075224fad","e99328bf818c774628ea5f2db597ac2250ad2068e5192f04c3bc96f39417ea55",S_LOC),"SynergyNet location correction drift")

def verify_location(v,kind):
    if kind=="nexus": exp=(N_LOC,N_ART,N_SIZE,N_MAN,N_RECIPE,N_EVID,N_FILE,"Shtenco/agi_nexus")
    else: exp=(S_LOC,S_ART,S_SIZE,S_MAN,S_RECIPE,S_EVID,S_FILE,"Shtenco/synergynet")
    selfhash(v,"location_evidence_digest",exp[0])
    req(v.get("schema")=="synergy.artifact-location-evidence/v2" and v.get("repository")==exp[7],"location identity drift")
    req((v.get("artifact_digest"),v.get("artifact_size"),v.get("artifact_manifest_digest"))==(exp[1],exp[2],exp[3]),"location artifact drift")
    req((v.get("build_recipe_digest"),v.get("build_evidence_digest"))==(exp[4],exp[5]),"location build binding drift")
    req(v.get("provider")=="GOOGLE_DRIVE_CONNECTED_FILE" and v.get("provider_file_id")==exp[6],"location provider drift")
    p=v.get("pre_upload_validation",{}); req((p.get("sha256"),p.get("size"),p.get("status"))==(exp[1],exp[2],"PASS"),"location pre-upload drift")
    req(v.get("integrity_model")=="CANONICAL_SELF_DIGEST_AND_FETCH_TIME_ARTIFACT_SHA256_SIZE","location integrity model drift")
    req(v.get("availability_status")=="DURABLE_CONNECTED_DRIVE_BINARY" and v.get("resolution_contract")=="FETCH_BY_PROVIDER_FILE_ID_THEN_VERIFY_SHA256_AND_SIZE_BEFORE_EXECUTION" and v.get("execution_authority")=="NONE","location contract drift")
    if kind=="nexus": req(v.get("runtime_spec_digest")==N_RUNTIME,"NEXUS location runtime binding drift")

def verify_nexus(build_input,recipe,evidence,runtime,location):
    selfhash(build_input,"build_input_digest",N_INPUT);selfhash(recipe,"recipe_digest",N_RECIPE);selfhash(evidence,"evidence_digest",N_EVID);selfhash(runtime,"runtime_spec_digest",N_RUNTIME);verify_location(location,"nexus")
    req((build_input.get("expected_artifact_digest"),build_input.get("expected_artifact_size"),build_input.get("expected_manifest_digest"))==(N_ART,N_SIZE,N_MAN),"NEXUS input output drift")
    req(recipe.get("schema")=="synergy.build-recipe/v4" and recipe.get("build_input_digest")==N_INPUT and recipe.get("artifact_digest")==N_ART and recipe.get("artifact_size")==N_SIZE and recipe.get("artifact_manifest_digest")==N_MAN,"NEXUS recipe drift")
    req(recipe.get("toolchain_lock_digest")==TOOL and recipe.get("builder_sha256")==BUILDER and recipe.get("reproducibility_status")=="REPRODUCIBLE_BYTE_IDENTICAL" and recipe.get("execution_authority")=="NONE","NEXUS recipe authority/toolchain drift")
    builds=evidence.get("builds",[]);req(evidence.get("schema")=="synergy.build-evidence/v2" and evidence.get("build_count")==2 and evidence.get("byte_identical") is True and len(builds)==2,"NEXUS build evidence drift")
    req(all((b.get("artifact_digest"),b.get("artifact_size"))==(N_ART,N_SIZE) for b in builds),"NEXUS build output drift")
    req(evidence.get("recipe_digest")==N_RECIPE and evidence.get("build_input_digest")==N_INPUT and all(x.get("status")=="PASS" for x in evidence.get("executed_smoke_tests",[])) and evidence.get("execution_authority")=="NONE","NEXUS evidence binding/smoke drift")
    req(runtime.get("schema")=="synergy.artifact-runtime-spec/v2" and runtime.get("artifact_digest")==N_ART,"NEXUS runtime identity drift")
    for f in ("network_access","process_execution_authority","financial_authority","execution_authority","remote_filesystem_path_authority"): req(runtime.get(f)=="NONE",f"NEXUS {f} escalation")

def verify_synergynet(recipe,evidence,content_runtime,relay_runtime,location):
    selfhash(recipe,"recipe_digest",S_RECIPE);selfhash(evidence,"evidence_digest",S_EVID);selfhash(content_runtime,"runtime_spec_digest",C_RUNTIME);selfhash(relay_runtime,"runtime_spec_digest",R_RUNTIME);verify_location(location,"synergynet")
    req(recipe.get("schema")=="synergy.build-recipe/v3" and recipe.get("artifact_digest")==S_ART and recipe.get("artifact_size")==S_SIZE and recipe.get("artifact_manifest_digest")==S_MAN,"SynergyNet recipe drift")
    req(recipe.get("toolchain_lock_digest")==TOOL and recipe.get("builder_sha256")==BUILDER and recipe.get("reproducibility_status")=="REPRODUCIBLE_BYTE_IDENTICAL" and recipe.get("execution_authority")=="NONE","SynergyNet recipe authority/toolchain drift")
    builds=evidence.get("builds",[]);req(evidence.get("build_count")==2 and evidence.get("byte_identical") is True and len(builds)==2 and all((b.get("artifact_digest"),b.get("artifact_size"))==(S_ART,S_SIZE) for b in builds),"SynergyNet build evidence drift")
    req(all(x.get("status")=="PASS" for x in evidence.get("executed_smoke_tests",[])) and evidence.get("execution_authority")=="NONE","SynergyNet smoke/authority drift")
    for spec,sid,d in ((content_runtime,"content-cache",C_RUNTIME),(relay_runtime,"synergynet",R_RUNTIME)):
        req(spec.get("schema")=="synergy.artifact-runtime-spec/v1" and spec.get("service_id")==sid and spec.get("artifact_digest")==S_ART and spec.get("runtime_spec_digest")==d and spec.get("execution_authority")=="NONE" and spec.get("remote_filesystem_path_authority")=="NONE",f"{sid} runtime drift")

def expected_services():
    common={"repository":"Shtenco/synergynet","artifact_digest":S_ART,"artifact_size":S_SIZE,"build_recipe_digest":S_RECIPE,"build_evidence_digest":S_EVID,"artifact_location_evidence_digest":S_LOC,"provider":"GOOGLE_DRIVE_CONNECTED_FILE","provider_file_id":S_FILE,"artifact_status":"VERIFIED_EXECUTABLE","reproducibility_status":"REPRODUCIBLE_BYTE_IDENTICAL","availability_status":"DURABLE_CONNECTED_DRIVE_BINARY","resolution_contract":"FETCH_BY_PROVIDER_FILE_ID_THEN_VERIFY_SHA256_AND_SIZE_BEFORE_EXECUTION","execution_authority":"NONE"}
    c={"service_id":"content-cache",**common,"artifact_runtime_spec_digest":C_RUNTIME};r={"service_id":"synergynet",**common,"artifact_runtime_spec_digest":R_RUNTIME}
    n={"service_id":"nexus","repository":"Shtenco/agi_nexus","artifact_digest":N_ART,"artifact_size":N_SIZE,"build_recipe_digest":N_RECIPE,"build_evidence_digest":N_EVID,"artifact_runtime_spec_digest":N_RUNTIME,"artifact_location_evidence_digest":N_LOC,"provider":"GOOGLE_DRIVE_CONNECTED_FILE","provider_file_id":N_FILE,"artifact_status":"VERIFIED_EXECUTABLE","reproducibility_status":"REPRODUCIBLE_BYTE_IDENTICAL","availability_status":"DURABLE_CONNECTED_DRIVE_BINARY","resolution_contract":"FETCH_BY_PROVIDER_FILE_ID_THEN_VERIFY_SHA256_AND_SIZE_BEFORE_EXECUTION","network_access":"NONE","process_execution_authority":"NONE","financial_authority":"NONE","execution_authority":"NONE","historical_artifact_digest":"fa7bbd141566d1542a5c03ee485de8ebd5f2ed76557ac56ff728196429fbbb64","lineage_transition":"V1_HISTORICAL_TO_V2_CURRENT_PRESERVE_HISTORY"}
    return [c,n,r]

def verify_readiness_v6(readiness,plan,aset,central_negative,location_negative,build_input,nexus_recipe,nexus_evidence,nexus_runtime,nexus_location,net_recipe,net_evidence,content_runtime,relay_runtime,net_location):
    verify_negatives(central_negative,location_negative);verify_nexus(build_input,nexus_recipe,nexus_evidence,nexus_runtime,nexus_location);verify_synergynet(net_recipe,net_evidence,content_runtime,relay_runtime,net_location)
    selfhash(aset,"artifact_set_digest",ASET);req(aset.get("schema")=="synergy.node-artifact-set/v4" and aset.get("previous_artifact_set_digest")=="bc7d89378424a18727b90072c86e06238ea14e64bfb9dfc4464f184297eddf84","artifact set ancestry drift")
    req(aset.get("central_self_digest_negative_evidence_digest")==CENTRAL_NEG and aset.get("location_evidence_self_digest_negative_evidence_digest")==LOCATION_NEG and aset.get("services")==expected_services(),"artifact set evidence bindings drift")
    req(aset.get("artifact_set_status")=="ALL_ARTIFACTS_VERIFIED_AND_DURABLY_LOCATABLE_WITH_CANONICAL_LOCATION_EVIDENCE" and aset.get("execution_authority")=="NONE","artifact set status drift")
    selfhash(plan,"plan_digest",PLAN);req(plan.get("schema")=="synergy.node-build-plan/v7" and plan.get("previous_build_plan_digest")=="74c32607bc9fdadf43dddc87c58aa58adeaa2d795553d02cba87cf55ca12ec98" and plan.get("artifact_set_digest")==ASET,"plan ancestry/root drift")
    req(plan.get("services")==expected_services() and plan.get("build_blockers")==[] and plan.get("plan_status")=="BUILD_ARTIFACTS_VERIFIED_REPRODUCIBLE_DURABLY_LOCATABLE_CANONICAL_LOCATION_EVIDENCE" and plan.get("execution_authority")=="NONE","plan evidence/status drift")
    selfhash(readiness,"readiness_digest",READY);req(readiness.get("schema")=="synergy.node-readiness/v6" and readiness.get("previous_readiness_digest")=="01c706352c6a63d8545373b29999dba9a9d3407bcf5c5e804e3e82a2571e2112","readiness ancestry drift")
    for f,e in (("profile_digest",PROFILE),("base_source_lock_digest",BASE),("source_revision_digest",REV),("build_plan_digest",PLAN),("toolchain_lock_digest",TOOL),("artifact_set_digest",ASET),("central_self_digest_negative_evidence_digest",CENTRAL_NEG),("location_evidence_self_digest_negative_evidence_digest",LOCATION_NEG)): req(readiness.get(f)==e,f"readiness {f} drift")
    req(readiness.get("blockers")==[] and readiness.get("node_status")=="NODE_ADMISSION_READY_NOT_RUNNING" and readiness.get("auto_start") is False,"readiness state drift")
    for f in ("financial_authority","payment_authority","accounting_authority","execution_authority"): req(readiness.get(f)=="NONE",f"readiness {f} escalation")
    return readiness
