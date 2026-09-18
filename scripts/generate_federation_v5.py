#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from federation_v5 import (
    EXCLUSIVE_AUTHORITIES,
    assert_valid_catalog,
    build_capability_registry,
    catalog_digest,
    load_catalog,
)

ROOT = Path(__file__).resolve().parents[1]
AUTO_COMPANY = "synergy_ai_company"
AUTO_COMPANY_RPC = [
    "autopilot.submit",
    "autopilot.status",
    "autopilot.approve",
    "autopilot.execute",
    "autopilot.capabilities",
    "nexus.runtime",
    "nexus.memory.search",
    "nexus.memory.upsert",
]


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_repository_registry(catalog: dict[str, Any]) -> dict[str, Any]:
    digest = catalog_digest(catalog)
    repos = sorted(catalog["repositories"], key=lambda r: str(r["name"]))
    return {
        "schema": "synergy.repository-registry/v5",
        "catalog_digest": digest,
        "repository_count": len(repos),
        "repositories": repos,
    }


def build_authority_map(catalog: dict[str, Any]) -> dict[str, Any]:
    digest = catalog_digest(catalog)
    repos = catalog["repositories"]
    exclusive: dict[str, str | None] = {}
    for authority in sorted(EXCLUSIVE_AUTHORITIES):
        owners = sorted(
            r["name"]
            for r in repos
            if r["lifecycle_status"] == "CANONICAL"
            and r["authority"].get(authority) == "CANONICAL"
        )
        exclusive[authority] = owners[0] if len(owners) == 1 else None
    return {
        "schema": "synergy.authority-map/v5",
        "catalog_digest": digest,
        "exclusive_authorities": exclusive,
        "repositories": {
            r["name"]: r["authority"]
            for r in sorted(repos, key=lambda x: x["name"])
        },
    }


def build_exchange_registry(catalog: dict[str, Any]) -> dict[str, Any]:
    source = json.loads(
        (ROOT / "config" / "exchange_object_registry_v1.json").read_text(encoding="utf-8")
    )
    source["catalog_digest"] = catalog_digest(catalog)
    source["objects"] = sorted(source["objects"], key=lambda x: x["name"])
    return source


def _trust_entry(repo: dict[str, Any], digest: str) -> dict[str, Any]:
    integration = "synergy.capability.v2"
    if repo["name"] == "agi_nexus":
        integration = "contract_only:inference_memory_sidecar_required"
    elif repo["name"] == "agi_autopilot":
        integration = "contract_only:executor_sidecar_required"
    return {
        "name": repo["name"],
        "repo": repo["repo_url"],
        "domain": repo["domain"],
        "risk_class": repo["risk_class"],
        "role": repo["role"],
        "integration": integration,
        "enabled": True,
        "capability_policy": "DENY",
        "rpc_allow": [],
        "transport_roles": [repo["role"]],
        "lifecycle_status": repo["lifecycle_status"],
        "system_kind": repo["system_kind"],
        "authority": repo["authority"],
        "capabilities_provided": repo["capabilities_provided"],
        "capabilities_consumed": repo["capabilities_consumed"],
        "allowed_exchange_objects": repo["allowed_exchange_objects"],
        "catalog_digest": digest,
    }


def build_trust_source(catalog: dict[str, Any]) -> dict[str, Any]:
    digest = catalog_digest(catalog)
    eligible = [
        r for r in catalog["repositories"]
        if r.get("trust_enabled") and r.get("federation_membership")
    ]
    repositories = [
        _trust_entry(r, digest)
        for r in sorted(eligible, key=lambda x: x["name"])
        if r["name"] != AUTO_COMPANY
    ]
    controls = []
    auto = next((r for r in eligible if r["name"] == AUTO_COMPANY), None)
    if auto:
        control = _trust_entry(auto, digest)
        control.update(
            integration="shttps.rpc/v1",
            capability_policy="ALLOWLIST",
            rpc_allow=AUTO_COMPANY_RPC,
        )
        controls.append(control)

    return {
        "schema": "synergy.federation-trust-source/v5",
        "owner": "Shtenco/synergy_system",
        "catalog_digest": digest,
        "policy": {
            "capability_default": "DENY",
            "repository_count": len(repositories),
            "control_principal_count": len(controls),
            "transport_authority": "NONE",
            "root_identity_policy": ["ML-DSA-87", "SLH-DSA-SHAKE-256s"],
            "high_impact_node_policy": ["ML-DSA-87", "SLH-DSA-SHAKE-256s"],
            "standard_node_policy": ["ML-DSA-87"],
            "node_default_lifetime_seconds": 7776000,
            "registry_max_lifetime_seconds": 2592000,
            "rotation_grace_seconds": 3600,
        },
        "repositories": repositories,
        "control_principals": controls,
    }


def build_graph(catalog: dict[str, Any], capabilities: dict[str, Any]) -> dict[str, Any]:
    digest = catalog_digest(catalog)
    provider = {
        c["capability"]: c["canonical_provider"]
        for c in capabilities["capabilities"]
    }
    edges: list[dict[str, str]] = []
    for repo in catalog["repositories"]:
        successor = repo.get("canonical_successor")
        if successor:
            edges.append({"from": repo["name"], "to": successor, "type": "canonical_successor"})
        for cap in repo.get("capabilities_consumed") or []:
            target = provider.get(cap)
            if target:
                edges.append({"from": repo["name"], "to": target, "type": "capability", "capability": cap})
    return {
        "schema": "synergy.federation-graph/v5",
        "catalog_digest": digest,
        "nodes": [
            {
                "name": r["name"],
                "lifecycle_status": r["lifecycle_status"],
                "system_kind": r["system_kind"],
                "trust_enabled": r["trust_enabled"],
            }
            for r in sorted(catalog["repositories"], key=lambda x: x["name"])
        ],
        "edges": sorted(edges, key=lambda e: (e["from"], e["to"], e["type"], e.get("capability", ""))),
    }


def status_matrix(catalog: dict[str, Any]) -> str:
    lines = [
        "# SYNERGY Federation V5 Repository Status Matrix",
        "",
        "Catalog digest: " + catalog_digest(catalog),
        "",
        "| Repository | Lifecycle | Kind | Domain | Trust | Successor |",
        "|---|---|---|---|---:|---|",
    ]
    for r in sorted(catalog["repositories"], key=lambda x: x["name"]):
        lines.append(
            "| {name} | {status} | {kind} | {domain} | {trust} | {successor} |".format(
                name=r["name"],
                status=r["lifecycle_status"],
                kind=r["system_kind"],
                domain=r["domain"],
                trust="YES" if r["trust_enabled"] else "NO",
                successor=r.get("canonical_successor") or "",
            )
        )
    return "\n".join(lines) + "\n"


def generate(output_dir: Path, catalog_path: Path) -> dict[str, Any]:
    catalog = load_catalog(catalog_path)
    assert_valid_catalog(catalog)
    output_dir.mkdir(parents=True, exist_ok=True)
    capability = build_capability_registry(catalog)
    outputs = {
        "repository_registry_v5.json": build_repository_registry(catalog),
        "authority_map_v5.json": build_authority_map(catalog),
        "capability_registry_v2.json": capability,
        "federation_trust_source_v5.json": build_trust_source(catalog),
        "exchange_object_registry_v1.json": build_exchange_registry(catalog),
        "federation_graph_v5.json": build_graph(catalog, capability),
    }
    for name, value in outputs.items():
        _write_json(output_dir / name, value)
    (output_dir / "FEDERATION_STATUS_MATRIX.md").write_text(status_matrix(catalog), encoding="utf-8")
    return outputs


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--catalog", default=str(ROOT / "config" / "repository_catalog_v5.json"))
    p.add_argument("--output-dir", default=str(ROOT / "generated"))
    args = p.parse_args()
    outputs = generate(Path(args.output_dir), Path(args.catalog))
    print(json.dumps({"ok": True, "catalog_digest": next(iter(outputs.values()))["catalog_digest"], "artifacts": sorted(outputs)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
