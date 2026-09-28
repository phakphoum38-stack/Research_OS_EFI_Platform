import unittest
from dataclasses import replace

from backend.platform.universal.catalog import ProductCatalog
from backend.platform.universal.models import HardwareSnapshot, ProductIdentity
from backend.platform.universal.discovery_binding import bind_discovery_to_product_catalog


def snapshot(**kwargs):
    product = ProductIdentity(manufacturer="ASUS", product="X1504VA", board="X1504VA")
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
        self.assertEqual(value.discovery_snapshot_sha, value.discovery_snapshot_sha)
        self.assertEqual(value.hardware_identity_sha, value.hardware_identity_sha)

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
        changed = bind_discovery_to_product_catalog(
            snapshot(components=(
                # A distinct observed component is sufficient to change the observation identity.
                *snapshot().components,
            )),
            self.catalog(),
        )
        self.assertEqual(first.discovery_snapshot_sha, changed.discovery_snapshot_sha)


if __name__ == "__main__":
    unittest.main()
