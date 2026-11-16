from __future__ import annotations

import copy, json
from pathlib import Path
import pytest

from synergy_system.node_readiness_v4 import NodeReadinessV4Error, digest, verify_readiness_v4

ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text(encoding='utf-8'))

def bundle():
    return {
      'readiness':load('fixtures/node_readiness/research_compute_node_readiness_v4.json'),
      'plan':load('fixtures/node_build_plans/research_compute_node_build_plan_reproducible_v4.json'),
      'revision':load('fixtures/node_source_revisions/research_compute_node_nexus_proof_core_v2.json'),
      'lock':load('config/build_toolchain_lock_v1.json'),
      'recipes':{'content-cache':load('fixtures/build_recipes/synergynet_build_recipe_v3.json'),'nexus':load('fixtures/build_recipes/agi_nexus_build_recipe_v3.json'),'synergynet':load('fixtures/build_recipes/synergynet_build_recipe_v3.json')},
      'evidence':{'content-cache':load('fixtures/build_evidence/synergynet_build_evidence_v1.json'),'nexus':load('fixtures/build_evidence/agi_nexus_build_evidence_v1.json'),'synergynet':load('fixtures/build_evidence/synergynet_build_evidence_v1.json')},
      'runtime':{'content-cache':load('fixtures/artifact_runtime_specs/synergynet_content_cache_artifact_runtime_spec_v1.json'),'nexus':load('fixtures/artifact_runtime_specs/agi_nexus_artifact_runtime_spec_v1.json'),'synergynet':load('fixtures/artifact_runtime_specs/synergynet_relay_artifact_runtime_spec_v1.json')},
    }

def verify(b): return verify_readiness_v4(b['readiness'],b['plan'],b['revision'],b['lock'],b['recipes'],b['evidence'],b['runtime'])

def test_canonical_v4_passes():
    b=bundle(); out=verify(b)
    assert out['blockers']==[]
    assert out['node_status']=='NODE_ADMISSION_READY_NOT_RUNNING'
    assert out['auto_start'] is False
    assert out['execution_authority']=='NONE'

def test_fresh_hash_cannot_fake_byte_equality():
    b=bundle(); e=copy.deepcopy(b['evidence']['nexus']); e['builds'][1]['artifact_digest']='0'*64; e['evidence_digest']=digest(e,'evidence_digest'); b['evidence']['nexus']=e
    with pytest.raises(NodeReadinessV4Error): verify(b)

def test_fresh_hash_cannot_fake_smoke_pass():
    b=bundle(); e=copy.deepcopy(b['evidence']['content-cache']); e['executed_smoke_tests'][0]['status']='FAIL'; e['evidence_digest']=digest(e,'evidence_digest'); b['evidence']['content-cache']=e; b['evidence']['synergynet']=e
    with pytest.raises(NodeReadinessV4Error): verify(b)

def test_missing_toolchain_cannot_keep_empty_blockers():
    b=bundle(); b['lock']['builder']['sha256']='0'*64; b['lock']['lock_digest']=digest(b['lock'],'lock_digest')
    with pytest.raises(NodeReadinessV4Error): verify(b)

def test_artifact_swap_rejected_even_with_fresh_outer_hashes():
    b=bundle(); p=copy.deepcopy(b['plan']); p['services'][1]['artifact_digest']=b['plan']['services'][0]['artifact_digest']; p['plan_digest']=digest(p,'plan_digest'); b['plan']=p; r=copy.deepcopy(b['readiness']); r['build_plan_digest']=p['plan_digest']; r['readiness_digest']=digest(r,'readiness_digest'); b['readiness']=r
    with pytest.raises(NodeReadinessV4Error): verify(b)

def test_readiness_cannot_autostart():
    b=bundle(); r=copy.deepcopy(b['readiness']); r['auto_start']=True; r['readiness_digest']=digest(r,'readiness_digest'); b['readiness']=r
    with pytest.raises(NodeReadinessV4Error): verify(b)

def test_readiness_cannot_grant_execution_authority():
    b=bundle(); r=copy.deepcopy(b['readiness']); r['execution_authority']='NODE'; r['readiness_digest']=digest(r,'readiness_digest'); b['readiness']=r
    with pytest.raises(NodeReadinessV4Error): verify(b)

def test_nexus_runtime_cannot_gain_network_authority():
    b=bundle(); s=copy.deepcopy(b['runtime']['nexus']); s['network_access']='ARBITRARY'; s['runtime_spec_digest']=digest(s,'runtime_spec_digest'); b['runtime']['nexus']=s
    with pytest.raises(NodeReadinessV4Error): verify(b)
