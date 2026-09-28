import json
import tempfile
import unittest
from pathlib import Path

from backend.platform.preflight import build_preflight


class M10PreflightTests(unittest.TestCase):
    def test_x1504va_profile_remains_blocked(self):
        profile = {
            "gpu": {"pci_id": "8086:A7A9", "acceleration_status": "not_proven"},
            "storage": {"vmd": {"ids": ["8086:09AB", "8086:A77F"], "status": "research"}},
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            oc = root / "OC"
            for name in ("ACPI", "Kexts", "Drivers", "Resources", "Tools"):
                (oc / name).mkdir(parents=True)
            (oc / "compatibility-report.json").write_text(
                json.dumps({"status": "EFI_BLOCKED"}), encoding="utf-8"
            )
            result = build_preflight(
                profile,
                str(root),
                {
                    "hypothesis": "X1504VA candidate can reach a controlled boot experiment",
                    "candidate_sha": "candidate-test-sha",
                    "status": "PLANNED",
                },
            )
            self.assertEqual(result["status"], "BLOCKED")
            self.assertFalse(result["mutation_performed"])
            self.assertTrue(any("gpu" in item for item in result["blockers"]))
            self.assertTrue(any("storage.vmd" in item for item in result["blockers"]))

    def test_ready_boundary_for_resolved_profile(self):
        profile = {
            "gpu": {"pci_id": "0000:0000", "acceleration_status": "proven"},
            "storage": {"vmd": {"ids": ["0000:0000"], "status": "proven"}},
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            oc = root / "OC"
            for name in ("ACPI", "Kexts", "Drivers", "Resources", "Tools"):
                (oc / name).mkdir(parents=True)
            (oc / "compatibility-report.json").write_text(
                json.dumps({"status": "READY"}), encoding="utf-8"
            )
            result = build_preflight(
                profile,
                str(root),
                {
                    "hypothesis": "controlled boot experiment",
                    "candidate_sha": "candidate-test-sha",
                    "status": "PLANNED",
                },
            )
            self.assertEqual(result["status"], "READY_FOR_HUMAN_BOOT")
            self.assertTrue(result["human_action_required"])
            self.assertFalse(result["mutation_performed"])


if __name__ == "__main__":
    unittest.main()
