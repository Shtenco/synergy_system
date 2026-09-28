#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GRAPH=json.loads((ROOT/"registry"/"DEPENDENCY_GRAPH.json").read_text(encoding="utf-8"))

def paths(source,target,edge_types):
    adj={}
    for e in GRAPH["edges"]:
        if e["type"] not in edge_types: continue
        adj.setdefault(e["from"],[]).append(e)
    q=deque([(source,[])])
    seen={(source,0)}
    out=[]
    while q:
        node,path=q.popleft()
        if len(path)>12: continue
        if node==target and path:
            out.append(path); continue
        for e in adj.get(node,[]):
            key=(e["to"],len(path)+1)
            if key in seen: continue
            seen.add(key);q.append((e["to"],path+[e]))
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("target")
    ap.add_argument("--type",action="append",dest="types")
    args=ap.parse_args()
    types=set(args.types or ["RUNTIME_DEPENDENCY","CONTRACT_FLOW"])
    found=paths(args.source,args.target,types)
    if not found:
        print("NO_PATH");return 1
    for i,path in enumerate(found,1):
        print(f"PATH {i}")
        for e in path:
            print(f"  {e['from']} --{e['type']}:{e.get('contract_id')}:{e.get('status')}--> {e['to']}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
