import unittest

from backend.platform.universal.identity import hardware_identity_sha, product_identity_sha
from backend.platform.universal.models import HardwareComponent, HardwareSnapshot, ProductIdentity
from backend.platform.universal.normalize import normalize_component, normalize_snapshot


class UniversalIdentityTests(unittest.TestCase):
    def test_product_identity_is_deterministic(self):
        identity = ProductIdentity(
            manufacturer="ASUS",
            product="X1504VA",
            board="X1504VA",
            board_version="1.0",
            bios_vendor="AMI",
            bios_version="313",
            cpu_model="Intel Core i3-1315U",
        )
        self.assertEqual(product_identity_sha(identity), product_identity_sha(identity))

    def test_hardware_identity_changes_when_stable_component_changes(self):
        base = HardwareSnapshot(
            platform="windows",
            product=ProductIdentity(manufacturer="ASUS", product="X1504VA", cpu_model="i3"),
            components=(
                HardwareComponent(kind="gpu", vendor="Intel", device_id="8086:A7A9", bus="pci"),
            ),
        )
        changed = HardwareSnapshot(
            platform="windows",
            product=base.product,
            components=(
                HardwareComponent(kind="gpu", vendor="Intel", device_id="8086:A788", bus="pci"),
            ),
        )
        self.assertNotEqual(hardware_identity_sha(base), hardware_identity_sha(changed))

    def test_normalization_is_stable(self):
        component = normalize_component(
            HardwareComponent(
                kind="GPU",
                name=" Intel   UHD ",
                device_id=r"PCI\VEN_8086&DEV_A7A9&SUBSYS_287D1043",
                bus="PCI",
            )
        )
        self.assertEqual(component.kind, "gpu")
        self.assertEqual(component.device_id, "8086:A7A9")

        snapshot = normalize_snapshot(
            HardwareSnapshot(
                platform=" Windows ",
                product=ProductIdentity(manufacturer=" ASUS ", product="X1504VA"),
                components=(component,),
            )
        )
        self.assertEqual(snapshot.platform, "windows")
        self.assertEqual(snapshot.product.manufacturer, "ASUS")


if __name__ == "__main__":
    unittest.main()