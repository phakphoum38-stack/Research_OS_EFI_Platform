import unittest

from backend.platform.universal.catalog import ProductCatalog
from backend.platform.universal.models import HardwareSnapshot, ProductIdentity


class UniversalCatalogTests(unittest.TestCase):
    def test_exact_product_and_board_match(self):
        catalog = ProductCatalog.from_dict(
            {
                "schema_version": "1.0",
                "products": [
                    {
                        "product_id": "asus-x1504va",
                        "manufacturer": "ASUS",
                        "product": "X1504VA",
                        "board": "X1504VA",
                    }
                ],
            }
        )
        snapshot = HardwareSnapshot(
            platform="windows",
            product=ProductIdentity(
                manufacturer="ASUS",
                product="X1504VA",
                board="X1504VA",
            ),
        )
        matches = catalog.match(snapshot)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].product_id, "asus-x1504va")
        self.assertIn("board", matches[0].matched_fields)


if __name__ == "__main__":
    unittest.main()
