import json
import tempfile
import unittest
from pathlib import Path

from backend.platform.research_case import ResearchCase
from backend.platform.runtime_evidence import RuntimeObservation, create_runtime_evidence, write_runtime_evidence
from backend.platform.runtime_learning import learn_from_runtime_evidence


class RuntimeLearningTests(unittest.TestCase):
    def test_runtime_evidence_updates_case_with_provenance(self):
        case = ResearchCase(
            "case-1", "source-sha", "X1504VA", "test hypothesis",
            facts=(), observations=(), provenance=(),
        )
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "runtime.txt"
            artifact.write_text("macOS runtime fixture\n", encoding="utf-8")
            evidence = create_runtime_evidence(
                "case-1", "source-sha", "candidate-sha", "INCONCLUSIVE", "macOS",
                [RuntimeObservation("graphics", "graphics observation", [str(artifact)])],
                [str(artifact)],
            )
            path = Path(tmp) / "runtime-evidence.json"
            write_runtime_evidence(evidence, str(path))
            evidence_id = json.loads(path.read_text(encoding="utf-8"))["evidence_id"]
            updated, knowledge = learn_from_runtime_evidence(case, str(path))

        self.assertEqual(len(knowledge.for_case("case-1")), 1)
        self.assertEqual(updated.observations[0]["observation_type"], "graphics")
        self.assertEqual(updated.provenance[0]["evidence_id"], evidence_id)

    def test_case_mismatch_is_rejected(self):
        case = ResearchCase("case-1", "source-sha", "X1504VA", "test", (), (), ())
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime-evidence.json"
            evidence = create_runtime_evidence(
                "case-2", "source-sha", "candidate-sha", "INCONCLUSIVE", "macOS",
                [RuntimeObservation("system", "observation")],
            )
            write_runtime_evidence(evidence, str(path))
            with self.assertRaises(ValueError):
                learn_from_runtime_evidence(case, str(path))


if __name__ == "__main__":
    unittest.main()
