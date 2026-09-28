import unittest

from backend.platform.universal.discovery import discover_product
from backend.platform.contracts import verify_envelope
from backend.platform.universal.identity import discovery_snapshot_sha, hardware_identity_sha
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
            metadata={"read_only": True},
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
        self.assertEqual(result.evidence.provenance["evidence_schema"], "discovery-v3")
        self.assertEqual(result.discovery_snapshot_sha, discovery_snapshot_sha(result.snapshot))
        self.assertEqual(result.evidence.payload["discovery_snapshot_sha"], result.discovery_snapshot_sha)
        self.assertFalse(result.evidence.provenance["physical_machine"])
        self.assertEqual(result.evidence.provenance["platform"], "windows")
        self.assertEqual(result.evidence.provenance["collector"], "fixture-provider@1.0")
        self.assertTrue(result.evidence.provenance["read_only"])
        self.assertTrue(verify_envelope(result.evidence.to_dict()))

    def test_snapshot_fingerprint_ignores_discovery_timestamp(self):
        first = FixtureProvider().discover()
        second = HardwareSnapshot(
            platform=first.platform,
            product=first.product,
            components=first.components,
            discovered_at="2030-01-01T00:00:00+00:00",
            metadata=first.metadata,
        )
        self.assertEqual(discovery_snapshot_sha(first), discovery_snapshot_sha(second))

    def test_source_pin_rejects_non_sha1_commit_value(self):
        with self.assertRaises(ValueError):
            discover_product(
                FixtureProvider(),
                source_sha="not-a-git-sha",
                source_pinned=True,
            )


if __name__ == "__main__":
    unittest.main()
