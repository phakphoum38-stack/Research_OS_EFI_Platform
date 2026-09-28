import unittest

from backend.platform.universal.catalog import ProductCatalog
from backend.platform.universal.discovery_binding import bind_discovery_to_product_catalog
from backend.platform.universal.models import HardwareComponent, HardwareSnapshot, ProductIdentity


def snapshot(**kwargs):
    product = kwargs.pop(
        "product",
        ProductIdentity(manufacturer="ASUS", product="X1504VA", board="X1504VA"),
    )
    return HardwareSnapshot(platform="windows", product=product, **kwargs)


class DiscoveryProductBindingTests(unittest.TestCase):
    def catalog(self):
        return ProductCatalog.from_dict({
            "schema_version": "1.0",
            "products": [{
                "product_id": "asus-x1504va",
                "manufacturer": "ASUS",
                "product": "X1504VA",
                "board": "X1504VA",
            }],
        })

    def test_exact_match_binds_deterministic_identities(self):
        value = bind_discovery_to_product_catalog(snapshot(), self.catalog())
        self.assertEqual(value.status, "MATCHED")
        self.assertEqual(value.matches[0].product_id, "asus-x1504va")
        self.assertTrue(value.discovery_snapshot_sha)
        self.assertTrue(value.hardware_identity_sha)

    def test_unmatched_is_explicit(self):
        value = bind_discovery_to_product_catalog(
            snapshot(product=ProductIdentity(manufacturer="ASUS", product="UNKNOWN")),
            self.catalog(),
        )
        self.assertEqual(value.status, "UNMATCHED")
        self.assertEqual(value.matches, ())

    def test_multiple_catalog_matches_are_ambiguous(self):
        catalog = ProductCatalog.from_dict({
            "products": [
                {"product_id": "a", "manufacturer": "ASUS", "product": "X1504VA"},
                {"product_id": "b", "manufacturer": "ASUS", "product": "X1504VA"},
            ]
        })
        value = bind_discovery_to_product_catalog(snapshot(), catalog)
        self.assertEqual(value.status, "AMBIGUOUS")

    def test_binding_changes_when_hardware_observation_changes(self):
        first = bind_discovery_to_product_catalog(snapshot(), self.catalog())
        changed_snapshot = snapshot(components=(
            HardwareComponent(
                kind="network",
                vendor="MediaTek",
                model="MT7902",
                device_id="14C3:7902",
                bus="pci",
            ),
        ))
        changed = bind_discovery_to_product_catalog(changed_snapshot, self.catalog())
        self.assertNotEqual(first.discovery_snapshot_sha, changed.discovery_snapshot_sha)
        self.assertNotEqual(first.hardware_identity_sha, changed.hardware_identity_sha)


if __name__ == "__main__":
    unittest.main()
