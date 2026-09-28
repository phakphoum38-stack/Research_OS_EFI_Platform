import tempfile
import unittest
from pathlib import Path

from backend.platform.acpi import find_nodes
from backend.platform.evidence import EvidenceLevel, EvidenceManifest
from backend.platform.manifest import build_manifest


class PlatformCoreTests(unittest.TestCase):
    def test_acpi_extracts_x1504va_nodes(self):
        dsl = [
            "Scope (\\_SB.PC00)", "{",
            "    Device (GFX0)", "{",
            "        Name (_ADR, 0x00020000)", "    }",
            "    Device (VMD0)", "{",
            "        Name (_ADR, 0x000E0000)",
            "        Device (NVD1)", "{",
            "            Name (_ADR, 0x02)", "        }",
            "    }", "}",
        ]
        nodes = find_nodes(dsl, {"GFX0", "VMD0", "NVD1"})
        self.assertEqual({n.name for n in nodes}, {"GFX0", "VMD0", "NVD1"})
        self.assertIn("0x000E0000", {n.adr for n in nodes})

    def test_manifest_keeps_unproven_devices_observed(self):
        profile = {
            "machine": "ASUS Vivobook X1504VA",
            "cpu": {"model": "Intel Core i3-1315U", "status": "proven"},
            "gpu": {"pci_id": "8086:A7A9", "acceleration_status": "not_proven"},
            "storage": {"vmd": {"ids": ["8086:09AB", "8086:A77F"], "status": "research"}},
        }
        levels = {item.subject: item.level for item in EvidenceManifest.from_profile(profile).evidence}
        self.assertEqual(levels["gpu"], EvidenceLevel.OBSERVED)
        self.assertEqual(levels["vmd"], EvidenceLevel.OBSERVED)

    def test_manifest_hashes_source_file(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "evidence.txt"
            source.write_text("x1504va", encoding="utf-8")
            manifest = build_manifest({"machine": "X1504VA"}, [str(source)])
            self.assertEqual(manifest["sources"][0]["size"], 7)
            self.assertRegex(manifest["sources"][0]["sha256"], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
