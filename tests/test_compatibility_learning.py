import tempfile
import unittest
from pathlib import Path

from backend.platform.compatibility_learning import compatibility_decisions_from_runtime_evidence
from backend.platform.runtime_evidence import RuntimeObservation, create_runtime_evidence, write_runtime_evidence


class CompatibilityLearningTests(unittest.TestCase):
    def write(self, tmp, result, platform, statement, kind="graphics"):
        evidence = create_runtime_evidence(
            "case-1", "source-sha", "candidate-sha", result, platform,
            [RuntimeObservation(kind, statement)],
        )
        path = Path(tmp) / "evidence.json"
        write_runtime_evidence(evidence, str(path))
        return path

    def test_only_explicit_passed_macos_observation_promotes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(
                tmp, "PASSED", "macOS",
                "Intel UHD 8086:A7A9 acceleration verified",
            )
            decisions = compatibility_decisions_from_runtime_evidence(str(path))

        self.assertEqual(len(decisions), 1)
        self.assertEqual(decisions[0].level.value, "MACOS_PROVEN")
        self.assertEqual(decisions[0].component, "gpu")
        self.assertEqual(decisions[0].evidence_id, decisions[0].evidence_id)

    def test_inconclusive_never_promotes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(
                tmp, "INCONCLUSIVE", "macOS",
                "Intel UHD 8086:A7A9 acceleration verified",
            )
            decisions = compatibility_decisions_from_runtime_evidence(str(path))
        self.assertEqual(decisions, [])

    def test_unrecognized_statement_never_promotes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(
                tmp, "PASSED", "macOS",
                "graphics appear functional",
            )
            decisions = compatibility_decisions_from_runtime_evidence(str(path))
        self.assertEqual(decisions, [])

    def test_non_macos_never_promotes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write(
                tmp, "PASSED", "Windows",
                "Intel UHD 8086:A7A9 acceleration verified",
            )
            decisions = compatibility_decisions_from_runtime_evidence(str(path))
        self.assertEqual(decisions, [])


if __name__ == "__main__":
    unittest.main()
