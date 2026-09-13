#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else 'config/federation_trust_source_v1.json')
d=json.loads(p.read_text(encoding='utf-8'))
assert d['schema']=='synergy.federation-trust-source/v1'
repos=d['repositories']; assert len(repos)==51, len(repos)
names=[x['name'] for x in repos]; assert len(set(names))==51
urls=[x['repo'] for x in repos]; assert len(set(urls))==51
for r in repos:
    assert r['name'] and r['repo'].startswith('https://github.com/Shtenco/')
    assert r['capability_policy'] in {'DENY','ALLOWLIST'}
    if r['capability_policy']=='DENY': assert r['rpc_allow']==[]
assert next(x for x in repos if x['name']=='agi_autopilot')['rpc_allow']==[
 'autopilot.submit','autopilot.status','autopilot.approve','autopilot.execute','autopilot.capabilities']
assert next(x for x in repos if x['name']=='agi_nexus')['rpc_allow']==[
 'nexus.runtime','nexus.memory.search','nexus.memory.upsert']
print(json.dumps({'ok':True,'repositories':len(repos),'deny_by_default':sum(not x['rpc_allow'] for x in repos)}))
