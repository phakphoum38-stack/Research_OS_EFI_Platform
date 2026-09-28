import unittest

from backend.platform.universal.discovery import discover_product
from backend.platform.universal.identity import hardware_identity_sha
from backend.platform.universal.models import HardwareComponent, HardwareSnapshot, ProductIdentity


class FixtureProvider:
    platform = "windows"
    name = "fixture-provider"
    version = "1.0"

    def discover(self):
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
                    kind="gpu",
                    name="Intel UHD Graphics",
                    vendor="Intel",
                    device_id=r"PCI\VEN_8086&DEV_A7A9",
                    bus="pci",
                ),
                HardwareComponent(
                    kind="storage",
                    name="KIOXIA KBG60ZNS512G",
                    vendor="KIOXIA",
                    model="KIOXIA KBG60ZNS512G",
                ),
            ),
        )


class UniversalDiscoveryFixtureTests(unittest.TestCase):
    def test_discovery_normalizes_and_wraps_evidence(self):
        result = discover_product(
            FixtureProvider(),
            source_sha="0123456789abcdef0123456789abcdef01234567",
            source_pinned=True,
        )
        self.assertEqual(result.snapshot.product.product, "X1504VA")
        self.assertEqual(
            result.hardware_identity_sha,
            hardware_identity_sha(result.snapshot),
        )
        self.assertTrue(result.evidence.evidence_id)
        self.assertTrue(result.snapshot.source_pinned)
        self.assertEqual(result.evidence.kind, "hardware-discovery")

    def test_source_pin_rejects_non_sha1_commit_value(self):
        with self.assertRaises(ValueError):
            discover_product(
                FixtureProvider(),
                source_sha="not-a-git-sha",
                source_pinned=True,
            )


if __name__ == "__main__":
    unittest.main()
