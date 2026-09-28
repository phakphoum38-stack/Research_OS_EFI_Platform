import json
import tempfile
import unittest
from pathlib import Path

from backend.platform.runtime_evidence import (
    RuntimeObservation,
    create_runtime_evidence,
    envelope_for_runtime,
    load_and_verify_runtime_evidence,
    write_runtime_evidence,
)


class RuntimeEvidenceTests(unittest.TestCase):
    def test_controlled_evidence_is_verifiable(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "runtime.txt"
            artifact.write_text("macOS runtime observation\n", encoding="utf-8")
            evidence = create_runtime_evidence(
                "x1504va-gpu-runtime",
                "source-sha",
                "candidate-sha",
                "INCONCLUSIVE",
                "macOS",
                [RuntimeObservation("graphics", "System reached graphical session; acceleration not yet proven.")],
                [str(artifact)],
            )
            envelope = envelope_for_runtime(evidence).to_dict()
            self.assertEqual(envelope["kind"], "runtime-evidence")
            self.assertEqual(envelope["status"], "INCONCLUSIVE")
            self.assertTrue(envelope["evidence_id"])

    def test_hardware_mutation_is_rejected(self):
        evidence = create_runtime_evidence(
            "case", "source", "candidate", "PASSED", "macOS",
            [RuntimeObservation("boot", "Observed controlled boot.")],
        )
        evidence.hardware_mutation_performed = True
        with self.assertRaises(ValueError):
            evidence.validate()

    def test_written_evidence_round_trips(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "runtime-evidence.json"
            evidence = create_runtime_evidence(
                "case", "source", "candidate", "FAILED", "macOS",
                [RuntimeObservation("storage", "Storage device not visible in runtime.")],
            )
            write_runtime_evidence(evidence, str(output))
            loaded = load_and_verify_runtime_evidence(str(output))
            self.assertEqual(loaded["payload"]["result"], "FAILED")
            self.assertEqual(loaded["payload"]["candidate_sha"], "candidate")


if __name__ == "__main__":
    unittest.main()
