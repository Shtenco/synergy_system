from __future__ import annotations
import hashlib, json
from pathlib import Path

EXPECTED='be8ca90e514e72ddccdc67a38cdd9b8321c2b55eb17ba6f04a9c65dbd4a16129'
ROOT=Path(__file__).resolve().parents[1]


def canonical(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()

def verify(v):
    p=dict(v); claimed=p.pop('release_manifest_digest',None)
    actual=hashlib.sha256(canonical(p)).hexdigest()
    if claimed!=EXPECTED or actual!=EXPECTED: raise ValueError('release digest mismatch')
    checks={
      'previous_preproduction_release_digest':'03914c9199b25227026d02a2a2b2d0d8a11e958982c76865701729fff55710ba',
      'synergynet_location_evidence_v3_digest':'b1ca1c1f5849deac30a0aac14748c21b8a74a26776ba2134a448c9427a839220',
      'synergynet_artifact_sha256':'7f22e68d80a7df879af71ebccdb45f8edb10cae3698bf07faa7076ce76fd0ef7',
      'artifact_resolution_status':'RESOLVED_CURRENT_GITHUB_GIT_CARRIER',
      'artifact_identity_status':'UNCHANGED_EXACT_REPRODUCIBLE',
      'release_stage':'PREPRODUCTION_RC3_ARTIFACT_RESOLUTION_RESTORED_NOT_PRODUCTION',
      'github_ci_status':'NOT_EXECUTED_UNKNOWN_STEPS_NULL',
      'nexus_network_access':'NONE',
    }
    for k,x in checks.items():
        if p.get(k)!=x: raise ValueError(f'{k} substitution')
    if p.get('current_running') is not False or p.get('auto_start') is not False: raise ValueError('running escalation')
    for k in ('financial_authority','payment_authority','accounting_authority','blockchain_submission_authority','execution_authority'):
        if p.get(k)!='NONE': raise ValueError(f'authority escalation {k}')
    if len(p.get('production_requirements',[]))!=7: raise ValueError('production requirements drift')
    return actual

if __name__=='__main__':
    v=json.loads((ROOT/'releases'/'synergy_autopilot_v5_ai_node_preproduction_rc3.json').read_text())
    print(json.dumps({'status':'PASS','release_manifest_digest':verify(v)},sort_keys=True))
