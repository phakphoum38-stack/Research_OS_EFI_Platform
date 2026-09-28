from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping

from backend.platform.contracts import digest
from backend.platform.universal.models import HardwareSnapshot


@dataclass(frozen=True)
class KnowledgeNode:
    node_id: str
    kind: str
    identity: str
    attributes: Mapping[str, Any] = field(default_factory=dict)
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "kind": self.kind,
            "identity": self.identity,
            "attributes": dict(self.attributes),
            "provenance": dict(self.provenance),
        }


@dataclass(frozen=True)
class KnowledgeEdge:
    source_id: str
    relation: str
    target_id: str
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "relation": self.relation,
            "target_id": self.target_id,
            "provenance": dict(self.provenance),
        }


@dataclass
class HardwareKnowledgeGraph:
    nodes: dict[str, KnowledgeNode] = field(default_factory=dict)
    edges: set[KnowledgeEdge] = field(default_factory=set)

    def add_node(self, kind: str, identity: str, *, attributes: Mapping[str, Any] | None = None, provenance: Mapping[str, Any] | None = None) -> KnowledgeNode:
        if not kind.strip() or not identity.strip():
            raise ValueError("kind and identity are required")
        node_id = f"{kind}:{digest({'identity': identity, 'attributes': dict(attributes or {})})[:24]}"
        node = KnowledgeNode(node_id, kind, identity, dict(attributes or {}), dict(provenance or {}))
        existing = self.nodes.get(node_id)
        if existing is not None and existing != node:
            raise ValueError(f"conflicting knowledge node: {node_id}")
        self.nodes[node_id] = node
        return node

    def add_edge(self, source_id: str, relation: str, target_id: str, *, provenance: Mapping[str, Any] | None = None) -> KnowledgeEdge:
        if source_id not in self.nodes or target_id not in self.nodes:
            raise KeyError("both edge endpoints must exist")
        if not relation.strip():
            raise ValueError("relation is required")
        edge = KnowledgeEdge(source_id, relation, target_id, dict(provenance or {}))
        self.edges.add(edge)
        return edge

    def related(self, node_id: str, relation: str | None = None) -> tuple[KnowledgeEdge, ...]:
        return tuple(sorted(
            (e for e in self.edges if e.source_id == node_id and (relation is None or e.relation == relation)),
            key=lambda e: (e.relation, e.target_id),
        ))

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [self.nodes[k].to_dict() for k in sorted(self.nodes)],
            "edges": [e.to_dict() for e in sorted(self.edges, key=lambda x: (x.source_id, x.relation, x.target_id))],
        }


def graph_from_snapshot(snapshot: HardwareSnapshot) -> HardwareKnowledgeGraph:
    graph = HardwareKnowledgeGraph()
    product = snapshot.product
    product_node = graph.add_node(
        "product",
        f"{product.manufacturer}:{product.product}:{product.board}",
        attributes=product.to_dict(),
        provenance={"collector": snapshot.collector, "source_sha": snapshot.source_sha},
    )
    platform_node = graph.add_node("platform", snapshot.platform)
    graph.add_edge(product_node.node_id, "observed_on", platform_node.node_id, provenance={"source_sha": snapshot.source_sha})
    for component in snapshot.components:
        identity = ":".join(filter(None, (component.vendor, component.model, component.device_id, component.bus, component.name)))
        component_node = graph.add_node(
            component.kind,
            identity or component.kind,
            attributes=component.to_dict(),
            provenance={"collector": snapshot.collector, "source_sha": snapshot.source_sha},
        )
        graph.add_edge(product_node.node_id, "has_component", component_node.node_id, provenance={"source_sha": snapshot.source_sha})
    return graph
