import unittest

from backend.platform.research.cases import ResearchCaseEngine, ResearchCaseState
from backend.platform.research.models import EvidenceRequirement, ResearchGap


class ResearchCaseTests(unittest.TestCase):
    def test_case_is_derived_from_gap_and_keeps_requirements(self):
        gap = ResearchGap(
            gap_id="gap-1",
            subject="8086:A7A9",
            question="Can macOS accelerate this GPU?",
            requirements=(EvidenceRequirement("req-1", "8086:A7A9", "acceleration works", ("runtime",)),),
        )
        case = ResearchCaseEngine().create(gap, "Acceleration is possible")
        self.assertEqual(case.state, ResearchCaseState.PLANNED)
        self.assertEqual(case.requirement_ids, ("req-1",))
        self.assertTrue(case.case_id.startswith("case-"))

    def test_lifecycle_does_not_claim_truth(self):
        gap = ResearchGap("gap-2", "storage", "Is the path usable?")
        engine = ResearchCaseEngine()
        case = engine.create(gap, "The path may be usable").begin()
        case = case.record_evidence("evidence-1")
        self.assertEqual(case.state, ResearchCaseState.EVIDENCE_READY)
        self.assertEqual(case.resolve(conclusive=False).state, ResearchCaseState.INCONCLUSIVE)
        self.assertEqual(case.resolve(conflicted=True).state, ResearchCaseState.CONFLICTED)


if __name__ == "__main__":
    unittest.main()
