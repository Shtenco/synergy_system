from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
import pytest
from synergy_system.autopilot_ai_node_registry_v2 import RegistryV2Error,verify_registry_v2
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'config/nodes/synergy_autopilot_v5_ai_node_v2.json'
def load(): return json.loads(P.read_text())
def fresh(v):
 b=dict(v);b.pop('registry_entry_digest',None);v['registry_entry_digest']=hashlib.sha256(json.dumps(b,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest();return v
def test_registry_v2_passes():
 r=verify_registry_v2(load());assert r['lab_running_snapshot_status']=='RUNNING_VERIFIED';assert r['current_running'] is False
@pytest.mark.parametrize('field,value',[
 ('candidate_commit','0'*40),('integration_manifest_digest','0'*64),('synergynet_transport_binding_digest','0'*64),('meta_os_lab_deployment_evidence_digest','0'*64),('meta_os_lab_deployment_result_digest','0'*64),('claim_tier','PRODUCTION_RUNNING'),('current_running',True),('lab_final_state','RUNNING'),('production_status','RUNNING'),('production_blockers',[]),('nexus_network_access','FULL_EGRESS'),('auto_start',True),('financial_authority','TREASURY'),('payment_authority','METAPAY'),('blockchain_submission_authority','SIGN_AND_SUBMIT'),('execution_authority','ROOT')])
def test_fresh_hash_cannot_promote_lab_registry(field,value):
 v=copy.deepcopy(load());v[field]=value;fresh(v)
 with pytest.raises(RegistryV2Error): verify_registry_v2(v)
