#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0,str(SCRIPTS))

from federation_v5 import assert_valid_catalog, load_catalog
from generate_federation_v5 import generate

EXPECTED={
    "repository_registry_v5.json",
    "authority_map_v5.json",
    "capability_registry_v2.json",
    "federation_trust_source_v5.json",
    "exchange_object_registry_v1.json",
    "federation_graph_v5.json",
    "FEDERATION_STATUS_MATRIX.md",
}


def _inventory_names(path: Path) -> set[str]:
    data=json.loads(path.read_text(encoding="utf-8"))
    items=data.get("repositories")
    if not isinstance(items,list):
        raise ValueError("E_INVENTORY_FORMAT:repositories must be list")
    names=set()
    for item in items:
        if isinstance(item,str):
            names.add(item)
        elif isinstance(item,dict) and item.get("name"):
            names.add(str(item["name"]))
        else:
            raise ValueError("E_INVENTORY_FORMAT:invalid repository item")
    return names


def main() -> int:
    p=argparse.ArgumentParser(description="Verify Federation V5 policy and generated drift")
    p.add_argument("--catalog",default=str(ROOT/"config"/"repository_catalog_v5.json"))
    p.add_argument("--generated-dir",default=str(ROOT/"generated"))
    p.add_argument("--inventory-json")
    args=p.parse_args()

    catalog=load_catalog(args.catalog)
    assert_valid_catalog(catalog)
    errors=[]

    if args.inventory_json:
        observed=_inventory_names(Path(args.inventory_json))
        expected={str(r["name"]) for r in catalog["repositories"]}
        if observed!=expected:
            missing=sorted(observed-expected)
            stale=sorted(expected-observed)
            errors.append("E_INVENTORY_DRIFT:unregistered="+",".join(missing)+";missing_live="+",".join(stale))

    committed=Path(args.generated_dir)
    with tempfile.TemporaryDirectory() as td:
        temp=Path(td)
        generate(temp,Path(args.catalog))
        actual={p.name for p in committed.iterdir()} if committed.exists() else set()
        if actual!=EXPECTED:
            errors.append("E_GENERATED_SET:"+",".join(sorted(actual^EXPECTED)))
        for name in sorted(EXPECTED & actual):
            if (committed/name).read_bytes()!=(temp/name).read_bytes():
                errors.append("E_GENERATED_DRIFT:"+name)

    if errors:
        print(json.dumps({"ok":False,"errors":errors},ensure_ascii=False,indent=2))
        return 1

    print(json.dumps({
        "ok":True,
        "repositories":len(catalog["repositories"]),
        "generated_artifacts":len(EXPECTED),
        "live_inventory_checked":bool(args.inventory_json),
    },ensure_ascii=False))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
