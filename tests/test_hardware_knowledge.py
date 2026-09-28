import unittest

from backend.platform.hardware_knowledge import graph_from_snapshot
from backend.platform.universal.models import HardwareComponent, HardwareSnapshot, ProductIdentity


class HardwareKnowledgeTests(unittest.TestCase):
    def test_snapshot_becomes_product_platform_and_component_graph(self):
        snapshot = HardwareSnapshot(
            platform="windows",
            collector="fixture",
            source_sha="source-1",
            product=ProductIdentity(manufacturer="ASUS", product="X1504VA", board="X1504VA"),
            components=(
                HardwareComponent(kind="gpu", vendor="Intel", model="UHD", device_id="8086:A7A9"),
                HardwareComponent(kind="storage", vendor="KIOXIA", model="KBG60ZNS512G", bus="nvme"),
            ),
        )
        graph = graph_from_snapshot(snapshot)
        self.assertEqual(len(graph.nodes), 4)
        product = next(n for n in graph.nodes.values() if n.kind == "product")
        self.assertEqual(len(graph.related(product.node_id)), 3)
        self.assertTrue(any(e.relation == "has_component" for e in graph.related(product.node_id)))

    def test_conflicting_nodes_are_not_silently_replaced(self):
        from backend.platform.hardware_knowledge import HardwareKnowledgeGraph
        graph = HardwareKnowledgeGraph()
        a = graph.add_node("gpu", "8086:A7A9", attributes={"name": "UHD"})
        graph.add_node("gpu", "8086:A7A9", attributes={"name": "UHD"})
        self.assertEqual(graph.nodes[a.node_id].attributes["name"], "UHD")


if __name__ == "__main__":
    unittest.main()
