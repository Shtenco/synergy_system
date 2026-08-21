from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

from .validator import FederationError


@dataclass(frozen=True)
class ArchitectureGraph:
    artifact: dict[str, Any]

    @property
    def digest(self) -> str:
        return str(self.artifact["digest"])


def build_architecture_graph(federation: dict[str, Any]) -> ArchitectureGraph:
    repositories = federation.get("repositories")
    edges = federation.get("canonical_dependency_direction")
    if not isinstance(repositories, list) or not isinstance(edges, list):
        raise FederationError("federation repositories/edges missing")

    nodes = sorted(entry["repo"] for entry in repositories)
    node_set = set(nodes)
    graph: dict[str, set[str]] = {node: set() for node in nodes}
    edge_rows: list[dict[str, str]] = []
    for edge in edges:
        source, target, contract = edge["from"], edge["to"], edge["contract"]
        if source not in node_set or target not in node_set:
            raise FederationError("graph edge endpoint missing")
        graph[source].add(target)
        edge_rows.append({"from": source, "to": target, "contract": contract})
    edge_rows.sort(key=lambda row: (row["from"], row["to"], row["contract"]))

    components = _strongly_connected_components(graph)
    cyclic = [component for component in components if len(component) > 1]
    payload = {
        "schema": "synergy.architecture-graph/v2",
        "source_schema": federation.get("schema"),
        "nodes": nodes,
        "edges": edge_rows,
        "strongly_connected_components": components,
        "cyclic_components": cyclic,
        "authority": "PRESENTATION_AND_GOVERNANCE_ONLY",
        "execution_authority": "NONE",
    }
    digest = hashlib.sha256(_canonical(payload)).hexdigest()
    return ArchitectureGraph(payload | {"digest": digest})


def to_dot(graph: ArchitectureGraph) -> str:
    artifact = graph.artifact
    lines = ["digraph synergy_federation {", "  rankdir=LR;"]
    for node in artifact["nodes"]:
        lines.append(f'  "{_dot_escape(node)}";')
    for edge in artifact["edges"]:
        label = _dot_escape(edge["contract"])
        lines.append(f'  "{_dot_escape(edge["from"])}" -> "{_dot_escape(edge["to"])}" [label="{label}"];')
    lines.append("}")
    return "\n".join(lines) + "\n"


def _strongly_connected_components(graph: dict[str, set[str]]) -> list[list[str]]:
    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    result: list[list[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlink[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for target in sorted(graph[node]):
            if target not in indices:
                visit(target)
                lowlink[node] = min(lowlink[node], lowlink[target])
            elif target in on_stack:
                lowlink[node] = min(lowlink[node], indices[target])
        if lowlink[node] == indices[node]:
            component: list[str] = []
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.append(member)
                if member == node:
                    break
            result.append(sorted(component))

    for node in sorted(graph):
        if node not in indices:
            visit(node)
    result.sort(key=lambda component: component[0])
    return result


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _dot_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
