from __future__ import annotations
import hashlib,json
from pathlib import Path
EXPECTED='84aa01ceec78a0ac112e6df30fe6953d519ab3f796fd565d80a4cd148b7eedb5'
EXPECTED_ROOTS={
 'synergynet_location_evidence_v3':'b1ca1c1f5849deac30a0aac14748c21b8a74a26776ba2134a448c9427a839220',
 'synergynet_transport_binding_v2':'0c58185ea0af4a8abc7ce215c0b7ff077cea9357e831b9d197ec730a34ed6c7e',
 'preproduction_rc3':'be8ca90e514e72ddccdc67a38cdd9b8321c2b55eb17ba6f04a9c65dbd4a16129',
 'production_bootstrap_v3':'00330d77273e5dd35ef7ba30cfe02a4cc4aef89522e374d1fb2ef833c318aa75',
 'meta_profile_v3':'96ea31f50ff61b478390d682e88cca89c806e88dbaef1c4fc53b109724ca8222',
 'meta_admission_v3':'b1c151d4d5095278006d338c65f3a56b4853c3b3aa70a429205bea84fc5770e8',
 'federation_registry_v3':'af24fe8c4b3ddfd8832f7e5ac6d92b2d4d69761cb9ab869407cd4d085e475526',
 'preproduction_rc4':'a7239ebf88b07f41b390120e3b3e23448e28548b3b9d981eb80a1fc014325803',
 'production_bootstrap_v4':'39d262d4d6b28ceba3f6ffacadebd79d023e214ba63db6dbef6f5a3ad15547c6',
}
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def verify(v):
 p=dict(v);claimed=p.pop('audit_digest',None);actual=hashlib.sha256(canonical(p)).hexdigest()
 if claimed!=EXPECTED or actual!=EXPECTED:raise ValueError('audit digest mismatch')
 roots={x['name']:x['digest'] for x in p.get('roots',[]) if x.get('status')=='PASS'}
 if roots!=EXPECTED_ROOTS:raise ValueError('root audit content mismatch')
 if p.get('pass_count')!=9 or p.get('fail_count')!=0:raise ValueError('audit counts mismatch')
 if p.get('github_ci_interpretation')!='NOT_EXECUTED_UNKNOWN_WHERE_JOBS_HAVE_STEPS_NULL_AND_LOGS_URL_NULL':raise ValueError('CI interpretation drift')
 if p.get('current_running') is not False or p.get('production_status')!='NOT_DEPLOYED' or p.get('execution_authority')!='NONE':raise ValueError('claim escalation')
 return actual
if __name__=='__main__':
 root=Path(__file__).resolve().parents[1];v=json.loads((root/'evidence'/'synergy_autopilot_v5_ai_node_rc4_root_audit_v1.json').read_text());print(json.dumps({'status':'PASS','audit_digest':verify(v)},sort_keys=True))
