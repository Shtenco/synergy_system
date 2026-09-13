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
    assert r['capability_policy']=='DENY' and r['rpc_allow']==[]
principals=d.get('control_principals') or []
assert len(principals)==1
c=principals[0]
assert c['name']=='synergy_ai_company' and c['capability_policy']=='ALLOWLIST'
assert set(c['rpc_allow'])=={
 'autopilot.submit','autopilot.status','autopilot.approve','autopilot.execute','autopilot.capabilities',
 'nexus.runtime','nexus.memory.search','nexus.memory.upsert'}
print(json.dumps({'ok':True,'repositories':len(repos),'control_principals':len(principals),'repository_rpc_deny':sum(not x['rpc_allow'] for x in repos),'control_routes':len(c['rpc_allow'])}))
