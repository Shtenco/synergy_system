from __future__ import annotations
import hashlib,json
from pathlib import Path
EXPECTED='af24fe8c4b3ddfd8832f7e5ac6d92b2d4d69761cb9ab869407cd4d085e475526'
BLOCKERS=['PRODUCTION_HOST_PROFILE_NOT_BOUND','PRODUCTION_SUPERVISOR_CONFIG_NOT_MATERIALIZED','PRODUCTION_DEPLOYMENT_EVIDENCE_NOT_EXECUTED']

def canonical(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def verify(v):
 p=dict(v); claimed=p.pop('registry_entry_digest',None); actual=hashlib.sha256(canonical(p)).hexdigest()
 if claimed!=EXPECTED or actual!=EXPECTED: raise ValueError('registry digest mismatch')
 checks={
  'previous_registry_entry_digest':'12bdca330d81b81ec0acb32cf974f12fb36c5e72e6a1fea8680dc5e8470b275d',
  'integration_manifest_digest':'a793250aaa2299fdaf1661e985423c2b62687a19395ceabcc7bb63c005defe54',
  'nexus_artifact_sha256':'e87d00809ff976c76655b892166ec1cf1f13a893927ead156295b6814fcd9325',
  'synergynet_artifact_sha256':'7f22e68d80a7df879af71ebccdb45f8edb10cae3698bf07faa7076ce76fd0ef7',
  'synergynet_location_evidence_v3_digest':'b1ca1c1f5849deac30a0aac14748c21b8a74a26776ba2134a448c9427a839220',
  'synergynet_transport_binding_v2_digest':'0c58185ea0af4a8abc7ce215c0b7ff077cea9357e831b9d197ec730a34ed6c7e',
  'meta_os_profile_v3_digest':'96ea31f50ff61b478390d682e88cca89c806e88dbaef1c4fc53b109724ca8222',
  'meta_os_admission_v3_digest':'b1c151d4d5095278006d338c65f3a56b4853c3b3aa70a429205bea84fc5770e8',
  'production_bootstrap_v3_digest':'00330d77273e5dd35ef7ba30cfe02a4cc4aef89522e374d1fb2ef833c318aa75',
  'preproduction_release_v3_digest':'be8ca90e514e72ddccdc67a38cdd9b8321c2b55eb17ba6f04a9c65dbd4a16129',
  'claim_tier':'PREPRODUCTION_RC3_STRUCTURALLY_ALIGNED_NOT_PRODUCTION',
  'artifact_resolution_status':'RESOLVED_CURRENT_GITHUB_GIT_CARRIER',
  'nexus_network_access':'NONE'
 }
 for k,x in checks.items():
  if p.get(k)!=x: raise ValueError(f'{k} substitution')
 if p.get('production_blockers')!=BLOCKERS: raise ValueError('production blocker drift')
 if p.get('current_running') is not False or p.get('auto_start') is not False: raise ValueError('running escalation')
 for k in ('financial_authority','payment_authority','accounting_authority','host_execution_authority','blockchain_submission_authority','execution_authority'):
  if p.get(k)!='NONE': raise ValueError(f'authority escalation {k}')
 return actual
def load_default(root=None):
 root=root or Path(__file__).resolve().parents[2]; return json.loads((root/'config'/'nodes'/'synergy_autopilot_v5_ai_node_v3.json').read_text())
