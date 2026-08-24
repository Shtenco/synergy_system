from __future__ import annotations
import hashlib, json
from pathlib import Path

EXPECTED_DIGEST = "0dd56320df6a1e18a7f77470b0609f55cb9c134ac67bbedeebdd3600e724124b"
EXPECTED_FIXED = {
    "schema": "synergy.ai-node-preproduction-release/v5",
    "release_id": "SYNERGY_AUTOPILOT_V5_AI_NODE_PREPRODUCTION_RC5_20260824",
    "node_id": "synergy-autopilot-v5-ai-node",
    "previous_preproduction_release_digest": "a7239ebf88b07f41b390120e3b3e23448e28548b3b9d981eb80a1fc014325803",
    "federation_registry_v3_digest": "af24fe8c4b3ddfd8832f7e5ac6d92b2d4d69761cb9ab869407cd4d085e475526",
    "integration_manifest_digest": "a793250aaa2299fdaf1661e985423c2b62687a19395ceabcc7bb63c005defe54",
    "deployment_reference_v2_digest": "87b9bb8158652dacc02832b465d94fddabfd31c9c6f5aa20bc9687b456bae879",
    "nexus_artifact_sha256": "e87d00809ff976c76655b892166ec1cf1f13a893927ead156295b6814fcd9325",
    "synergynet_artifact_sha256": "7f22e68d80a7df879af71ebccdb45f8edb10cae3698bf07faa7076ce76fd0ef7",
    "synergynet_location_evidence_v3_digest": "b1ca1c1f5849deac30a0aac14748c21b8a74a26776ba2134a448c9427a839220",
    "synergynet_transport_binding_v2_digest": "0c58185ea0af4a8abc7ce215c0b7ff077cea9357e831b9d197ec730a34ed6c7e",
    "meta_os_profile_v3_digest": "96ea31f50ff61b478390d682e88cca89c806e88dbaef1c4fc53b109724ca8222",
    "meta_os_admission_v3_digest": "b1c151d4d5095278006d338c65f3a56b4853c3b3aa70a429205bea84fc5770e8",
    "production_bootstrap_v4_digest": "39d262d4d6b28ceba3f6ffacadebd79d023e214ba63db6dbef6f5a3ad15547c6",
    "ai_blockchain_preproduction_commitment_v3_digest": "608b0ca91e905cb0345d345af9e1246489236a8e672a07fb60ea4cfb8691d397",
    "artifact_resolution_status": "RESOLVED_CURRENT_GITHUB_GIT_CARRIER",
    "federation_alignment_status": "ALL_CURRENT_PREPRODUCTION_DOMAINS_ALIGNED_DEPLOYMENT_REFERENCE_V2_BLOCKCHAIN_COMMITMENT_V3",
    "release_stage": "PREPRODUCTION_RC5_FULL_DOMAIN_CLOSURE_READY_FOR_REAL_PRODUCTION_HOST_BINDING",
    "current_running": False,
    "auto_start": False,
    "nexus_network_access": "NONE",
    "github_ci_status": "NOT_EXECUTED_UNKNOWN_STEPS_NULL",
    "financial_authority": "NONE",
    "payment_authority": "NONE",
    "accounting_authority": "NONE",
    "host_execution_authority": "NONE",
    "blockchain_submission_authority": "NONE",
    "execution_authority": "NONE"
}

class RC5Error(ValueError): pass

def canonical(v): return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()

def verify(v):
    if not isinstance(v, dict): raise RC5Error("release must be object")
    p = dict(v); claimed = p.pop("release_manifest_digest", None)
    actual = hashlib.sha256(canonical(p)).hexdigest()
    if claimed != EXPECTED_DIGEST or actual != EXPECTED_DIGEST: raise RC5Error("digest mismatch")
    for k, expected in EXPECTED_FIXED.items():
        if p.get(k) != expected: raise RC5Error(f"identity/state mismatch: {k}")
    req = p.get("production_requirements")
    if not isinstance(req, list) or len(req) != 7 or len(set(req)) != 7: raise RC5Error("requirements mismatch")
    return actual

def main():
    root = Path(__file__).resolve().parents[1]
    v = json.loads((root/"releases"/"synergy_autopilot_v5_ai_node_preproduction_rc5.json").read_text(encoding="utf-8"))
    print(json.dumps({"status":"PASS","release_manifest_digest":verify(v)}, sort_keys=True)); return 0

if __name__ == "__main__": raise SystemExit(main())
