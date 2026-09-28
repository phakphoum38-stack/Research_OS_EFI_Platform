import unittest

from backend.platform.universe.catalog import ObservedProduct, ProductCatalog, ProductModel, ProductVariant
from backend.platform.universe.conflicts import detect_conflicts


class ProductUniverseTests(unittest.TestCase):
    def product(self):
        return ProductModel("ASUS", "Vivobook", "X1504VA")

    def test_catalog_separates_model_variant_and_observation(self):
        catalog = ProductCatalog()
        model = self.product()
        catalog.add_model(model)
        catalog.add_variant(ProductVariant("x1504va-i3", model.key, {"cpu": "Intel Core i3-1315U"}))
        observation = ObservedProduct("obs-1", model, "x1504va-i3", "src-1", "2026-09-28T00:00:00Z", {"gpu": "8086:A7A9"})
        catalog.add_observation(observation)
        value = catalog.to_dict()
        self.assertEqual(len(value["models"]), 1)
        self.assertEqual(len(value["variants"]), 1)
        self.assertEqual(len(value["observations"]), 1)

    def test_same_model_different_hardware_is_conflict_not_duplicate_truth(self):
        model = self.product()
        items = (
            ObservedProduct("a", model, None, "src-a", "t1", {"storage": "KBG60ZNS512G"}),
            ObservedProduct("b", model, None, "src-b", "t2", {"storage": "OTHER"}),
        )
        conflicts = detect_conflicts(items)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0].fields, ("storage",))

    def test_variant_requires_known_model(self):
        catalog = ProductCatalog()
        with self.assertRaises(KeyError):
            catalog.add_variant(ProductVariant("v", "missing", {}))


if __name__ == "__main__":
    unittest.main()
