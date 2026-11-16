from __future__ import annotations
import hashlib,json
from typing import Any

REGISTRY_V1="bc232a6d919656f734d698f3b5b602436f736463f3970665262a9c954b45bab6"
REGISTRY_V2="12bdca330d81b81ec0acb32cf974f12fb36c5e72e6a1fea8680dc5e8470b275d"
NODE_COMMIT="c39f6f0ee0e37c08366a63ec160c580b9ae954ba"
NODE_ROOT="a793250aaa2299fdaf1661e985423c2b62687a19395ceabcc7bb63c005defe54"
TRANSPORT="3c8198e10863c52c0492ca422c404a1e05e6fd2f48f4c393587d9d87eee3855f"
META_PROFILE="6a84a2dd132823756c9f159b04584ac384dca9514316b3ff5c9f4ce06e1696d3"
META_ADMISSION="4d3502dba28745b8a734c082ca0260cbbfd4ead11a1396537434844df9987ee3"
LAB_HOST="36a9092977e360b56fd7d1e21b4504f1215ed741df6f492b3ed37b79649573bb"
LAB_SUPERVISOR="74797e02e0bb32722bbfffb76af42bb00d495fb3a5c0ea4a5b48a4e1d4275879"
LAB_EVIDENCE="8e1b05dca7e349d57e1908dca717d2c1d451ca79adde5cfe539e9e46f83d052b"
LAB_RESULT="011c3ce24cfd33dc99fbdea0ea2f5dcd344deefd927f57c1b9c1fa3e3eaa3833"
PROD_BLOCKERS=["PERSISTENT_PRODUCTION_HOST_NOT_BOUND","PRODUCTION_SUPERVISOR_NOT_MATERIALIZED","PRODUCTION_DEPLOYMENT_EVIDENCE_NOT_EXECUTED"]
class RegistryV2Error(ValueError): pass

def digest(v:dict[str,Any])->str:
 b=dict(v);b.pop('registry_entry_digest',None);return hashlib.sha256(json.dumps(b,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def verify_registry_v2(v):
 if v.get('schema')!='synergy.node-registry-entry/v2' or digest(v)!=v.get('registry_entry_digest') or v.get('registry_entry_digest')!=REGISTRY_V2: raise RegistryV2Error('digest')
 if v.get('previous_registry_entry_digest')!=REGISTRY_V1: raise RegistryV2Error('lineage')
 if v.get('candidate_commit')!=NODE_COMMIT or v.get('integration_manifest_digest')!=NODE_ROOT: raise RegistryV2Error('node')
 if v.get('synergynet_transport_binding_digest')!=TRANSPORT: raise RegistryV2Error('transport')
 expected={'meta_os_profile_digest':META_PROFILE,'meta_os_admission_digest':META_ADMISSION,'meta_os_lab_host_profile_digest':LAB_HOST,'meta_os_lab_supervisor_config_digest':LAB_SUPERVISOR,'meta_os_lab_deployment_evidence_digest':LAB_EVIDENCE,'meta_os_lab_deployment_result_digest':LAB_RESULT}
 for k,x in expected.items():
  if v.get(k)!=x: raise RegistryV2Error(k)
 if v.get('claim_tier')!='LAB_RUNNING_VERIFIED_STOPPED_AFTER_VERIFICATION_NOT_PRODUCTION': raise RegistryV2Error('claim')
 if v.get('lab_running_snapshot_status')!='RUNNING_VERIFIED' or v.get('lab_final_state')!='STOPPED_AFTER_VERIFICATION' or v.get('current_running') is not False: raise RegistryV2Error('state')
 if v.get('production_status')!='NOT_RUNNING_NO_PERSISTENT_PRODUCTION_HOST' or v.get('production_blockers')!=PROD_BLOCKERS: raise RegistryV2Error('production')
 if v.get('nexus_network_access')!='NONE' or v.get('auto_start') is not False: raise RegistryV2Error('runtime')
 for f in ('financial_authority','payment_authority','accounting_authority','host_execution_authority','blockchain_submission_authority','execution_authority'):
  if v.get(f)!='NONE': raise RegistryV2Error(f)
 return v
