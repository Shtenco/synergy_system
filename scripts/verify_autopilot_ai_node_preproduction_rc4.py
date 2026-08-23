from __future__ import annotations
import hashlib,json
from pathlib import Path
EXPECTED='a7239ebf88b07f41b390120e3b3e23448e28548b3b9d981eb80a1fc014325803'

def canonical(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def verify(v):
 p=dict(v);claimed=p.pop('release_manifest_digest',None);actual=hashlib.sha256(canonical(p)).hexdigest()
 if claimed!=EXPECTED or actual!=EXPECTED: raise ValueError('release digest mismatch')
 checks={
  'previous_preproduction_release_digest':'be8ca90e514e72ddccdc67a38cdd9b8321c2b55eb17ba6f04a9c65dbd4a16129',
  'federation_registry_v3_digest':'af24fe8c4b3ddfd8832f7e5ac6d92b2d4d69761cb9ab869407cd4d085e475526',
  'synergynet_location_evidence_v3_digest':'b1ca1c1f5849deac30a0aac14748c21b8a74a26776ba2134a448c9427a839220',
  'synergynet_transport_binding_v2_digest':'0c58185ea0af4a8abc7ce215c0b7ff077cea9357e831b9d197ec730a34ed6c7e',
  'meta_os_profile_v3_digest':'96ea31f50ff61b478390d682e88cca89c806e88dbaef1c4fc53b109724ca8222',
  'meta_os_admission_v3_digest':'b1c151d4d5095278006d338c65f3a56b4853c3b3aa70a429205bea84fc5770e8',
  'production_bootstrap_v3_digest':'00330d77273e5dd35ef7ba30cfe02a4cc4aef89522e374d1fb2ef833c318aa75',
  'federation_alignment_status':'LOCATION_V3_TRANSPORT_V2_META_PROFILE_V3_ADMISSION_V3_REGISTRY_V3_ALIGNED',
  'release_stage':'PREPRODUCTION_RC4_FEDERATION_ALIGNED_READY_FOR_PRODUCTION_HOST_BINDING',
  'artifact_resolution_status':'RESOLVED_CURRENT_GITHUB_GIT_CARRIER',
  'nexus_network_access':'NONE'
 }
 for k,x in checks.items():
  if p.get(k)!=x: raise ValueError(f'{k} substitution')
 if len(p.get('production_requirements',[]))!=7: raise ValueError('production requirements drift')
 if p.get('current_running') is not False or p.get('auto_start') is not False: raise ValueError('running escalation')
 for k in ('financial_authority','payment_authority','accounting_authority','host_execution_authority','blockchain_submission_authority','execution_authority'):
  if p.get(k)!='NONE': raise ValueError(f'authority escalation {k}')
 return actual
if __name__=='__main__':
 root=Path(__file__).resolve().parents[1];v=json.loads((root/'releases'/'synergy_autopilot_v5_ai_node_preproduction_rc4.json').read_text());print(json.dumps({'status':'PASS','release_manifest_digest':verify(v)},sort_keys=True))
