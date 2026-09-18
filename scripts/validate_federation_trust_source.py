#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "config/federation_trust_source_v1.json")
d=json.loads(p.read_text(encoding="utf-8"))
schema=d.get("schema")
assert schema in {"synergy.federation-trust-source/v1","synergy.federation-trust-source/v5"}, schema

repos=d.get("repositories") or []
names=[x["name"] for x in repos]
urls=[x["repo"] for x in repos]
assert len(names)==len(set(names)), "duplicate repository name"
assert len(urls)==len(set(urls)), "duplicate repository URL"

for r in repos:
    assert r["name"] and r["repo"].startswith("https://github.com/Shtenco/")
    assert r["capability_policy"]=="DENY"
    assert r["rpc_allow"]==[]
    if schema.endswith("/v5"):
        assert r["catalog_digest"]==d["catalog_digest"]
        assert r["lifecycle_status"] not in {"LEGACY","ARCHIVE"}

principals=d.get("control_principals") or []
assert len(principals)==1
c=principals[0]
assert c["name"]=="synergy_ai_company"
assert c["capability_policy"]=="ALLOWLIST"
assert set(c["rpc_allow"])=={
 "autopilot.submit","autopilot.status","autopilot.approve","autopilot.execute","autopilot.capabilities",
 "nexus.runtime","nexus.memory.search","nexus.memory.upsert"
}

policy=d.get("policy") or {}
assert int(policy.get("repository_count",-1))==len(repos), (
    policy.get("repository_count"),len(repos)
)
if schema.endswith("/v5"):
    assert int(policy.get("control_principal_count",-1))==len(principals)
    assert c["catalog_digest"]==d["catalog_digest"]

print(json.dumps({
    "ok":True,
    "schema":schema,
    "repositories":len(repos),
    "control_principals":len(principals),
    "repository_rpc_deny":sum(not x["rpc_allow"] for x in repos),
    "control_routes":len(c["rpc_allow"]),
    "catalog_digest":d.get("catalog_digest"),
},sort_keys=True))
