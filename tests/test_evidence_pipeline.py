import tempfile
import unittest
from pathlib import Path

from backend.platform.pipeline import build_evidence_packet, fingerprint_tree


class EvidencePipelineTests(unittest.TestCase):
    def test_x1504va_pipeline_is_blocked_but_inspectable(self):
        profile = {
            "machine": "ASUS Vivobook X1504VA",
            "gpu": {"pci_id": "8086:A7A9", "acceleration_status": "not_proven"},
            "storage": {
                "vmd": {
                    "ids": ["8086:09AB", "8086:A77F"],
                    "status": "research",
                }
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            packet = build_evidence_packet(
                profile,
                str(Path(tmp) / "EFI"),
                "a" * 40,
                "determine whether the X1504VA candidate can reach controlled boot",
            )
        self.assertEqual(packet["status"], "BLOCKED")
        self.assertEqual(packet["candidate"]["status"], "EFI_BLOCKED")
        self.assertEqual(packet["opencore_validation"]["status"], "PASS")
        self.assertFalse(packet["safety"]["mutation_performed"])
        self.assertFalse(packet["safety"]["hardware_mutation_authorized"])
        self.assertTrue(packet["candidate_sha"])
        self.assertEqual(
            packet["evidence_envelope"]["evidence_id"],
            __import__("backend.platform.contracts", fromlist=["digest"]).digest(
                {
                    "source_sha": packet["evidence_envelope"]["source_sha"],
                    "kind": packet["evidence_envelope"]["kind"],
                    "status": packet["evidence_envelope"]["status"],
                    "payload": packet["evidence_envelope"]["payload"],
                    "provenance": packet["evidence_envelope"]["provenance"],
                }
            ),
        )

    def test_fingerprint_changes_with_file_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a").write_bytes(b"one")
            first = fingerprint_tree(tmp)
            (root / "a").write_bytes(b"two")
            self.assertNotEqual(first, fingerprint_tree(tmp))


if __name__ == "__main__":
    unittest.main()
