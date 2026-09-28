import unittest

from backend.platform.compatibility_learning import CompatibilityDecision
from backend.platform.compatibility_update import build_proposal, verify_proposal
from backend.platform.evidence import EvidenceLevel


class CompatibilityUpdateTests(unittest.TestCase):
    def test_builds_provenance_rich_proposal_without_mutating_profile(self) -> None:
        decision = CompatibilityDecision(
            component="gpu",
            value="8086:A7A9",
            level=EvidenceLevel.MACOS_PROVEN,
            evidence_id="ev-123",
            case_id="case-123",
            source_sha="source-123",
            candidate_sha="candidate-123",
            reason="explicit controlled runtime promotion rule",
        )
        proposal = build_proposal(
            decision,
            current_value="8086:A7A9",
            current_level="RESEARCH",
        )
        self.assertEqual(proposal.proposed_level, "macos_proven")
        self.assertEqual(proposal.evidence_id, "ev-123")
        self.assertEqual(proposal.current_level, "RESEARCH")
        self.assertTrue(verify_proposal(proposal))

    def test_rejects_missing_provenance(self) -> None:
        decision = CompatibilityDecision(
            component="gpu",
            value="8086:A7A9",
            level=EvidenceLevel.MACOS_PROVEN,
            evidence_id="",
            case_id="case-123",
            source_sha="source-123",
            candidate_sha="candidate-123",
            reason="explicit controlled runtime promotion rule",
        )
        with self.assertRaises(ValueError):
            build_proposal(
                decision,
                current_value="8086:A7A9",
                current_level="RESEARCH",
            )


if __name__ == "__main__":
    unittest.main()
