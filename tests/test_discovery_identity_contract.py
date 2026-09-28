import unittest
from dataclasses import replace

from backend.platform.universal.identity import discovery_snapshot_sha
from backend.platform.universal.models import HardwareComponent, HardwareSnapshot, ProductIdentity


def make_snapshot():
    return HardwareSnapshot(
        platform="windows",
        product=ProductIdentity(
            manufacturer="ASUS",
            product="X1504VA",
            board="X1504VA",
            board_version="1.0",
            bios_vendor="AMI",
            bios_version="313",
            cpu_model="Intel Core i3-1315U",
        ),
        components=(
            HardwareComponent(
                kind="gpu", name="Intel UHD Graphics", vendor="Intel",
                device_id=r"PCI\VEN_8086&DEV_A7A9", bus="pci",
            ),
            HardwareComponent(
                kind="storage", name="KIOXIA KBG60ZNS512G", vendor="KIOXIA",
                model="KIOXIA KBG60ZNS512G", bus="nvme",
            ),
        ),
        discovered_at="2026-01-01T00:00:00+00:00",
        collector="fixture@1.0", source_pinned=True,
        source_sha="0123456789abcdef0123456789abcdef01234567",
        metadata={"read_only": True, "provider": "fixture", "physical_machine": False},
    )


class DiscoveryIdentityContractTests(unittest.TestCase):
    def test_timestamp_does_not_change_identity(self):
        first = make_snapshot()
        second = replace(first, discovered_at="2030-01-01T00:00:00+00:00")
        self.assertEqual(discovery_snapshot_sha(first), discovery_snapshot_sha(second))

    def test_provenance_does_not_change_identity(self):
        first = make_snapshot()
        second = replace(first, collector="other-provider@9.9", source_pinned=False,
                         source_sha="", metadata={"read_only": False, "provider": "other-provider",
                                                  "physical_machine": True})
        self.assertEqual(discovery_snapshot_sha(first), discovery_snapshot_sha(second))

    def test_component_order_does_not_change_identity(self):
        first = make_snapshot()
        second = replace(first, components=tuple(reversed(first.components)))
        self.assertEqual(discovery_snapshot_sha(first), discovery_snapshot_sha(second))

    def test_hardware_change_changes_identity(self):
        first = make_snapshot()
        changed = replace(first, components=first.components + (
            HardwareComponent(kind="network", name="MediaTek MT7902", vendor="MediaTek",
                              device_id="14C3:7902", bus="pci"),
        ))
        self.assertNotEqual(discovery_snapshot_sha(first), discovery_snapshot_sha(changed))

    def test_product_change_changes_identity(self):
        first = make_snapshot()
        changed = replace(first, product=replace(first.product, product="X1504VA-ALT"))
        self.assertNotEqual(discovery_snapshot_sha(first), discovery_snapshot_sha(changed))

    def test_schema_change_changes_identity(self):
        first = make_snapshot()
        changed = replace(first, schema_version="discovery-v2")
        self.assertNotEqual(discovery_snapshot_sha(first), discovery_snapshot_sha(changed))

    def test_platform_change_changes_identity(self):
        first = make_snapshot()
        changed = replace(first, platform="linux")
        self.assertNotEqual(discovery_snapshot_sha(first), discovery_snapshot_sha(changed))


if __name__ == "__main__":
    unittest.main()
