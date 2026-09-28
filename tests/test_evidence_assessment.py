import unittest

from backend.platform.research.evidence import assess_gap
from backend.platform.research.models import ResearchGap
from backend.platform.research.observations import ResearchObservation
from backend.platform.research.requirements import requirement_for_hardware_claim


class EvidenceAssessmentTests(unittest.TestCase):
    def setUp(self):
        req = requirement_for_hardware_claim(
            requirement_id="req-1", subject="device", claim="support", evidence_types=("upstream",)
        )
        self.gap = ResearchGap("gap-1", "device", "is it supported?", requirements=(req,))

    def obs(self, ident, supports):
        return ResearchObservation(ident, "gap-1", "src", ident, supports, "upstream")

    def test_no_observations_remains_research(self):
        result = assess_gap(self.gap, ())
        self.assertEqual(result.state, "RESEARCH")

    def test_support_is_not_automatically_proven(self):
        result = assess_gap(self.gap, (self.obs("obs-1", True),))
        self.assertEqual(result.state, "SUPPORTED")
        self.assertNotEqual(result.state, "PROVEN")

    def test_conflicting_observations_are_preserved(self):
        result = assess_gap(self.gap, (self.obs("yes", True), self.obs("no", False)))
        self.assertEqual(result.state, "CONFLICTED")
        self.assertEqual(result.supporting, ("yes",))
        self.assertEqual(result.contradicting, ("no",))


if __name__ == "__main__":
    unittest.main()
