import unittest

from backend.platform.research import (
    EvidenceRequirement,
    ResearchGap,
    ResearchObservation,
    ResearchRegistry,
    ResearchSource,
)
from backend.platform.research.observations import ObservationDisposition
from backend.platform.research.requirements import EvidenceRequirementStatus
from backend.platform.research.sources import SourceType


class ResearchFoundationTests(unittest.TestCase):
    def test_gap_identity_is_deterministic(self):
        a = ResearchGap("8086:A7A9", "Can macOS accelerate this GPU?", "acceleration is not proven", ("runtime", "upstream"))
        b = ResearchGap("8086:A7A9", "Can macOS accelerate this GPU?", "acceleration is not proven", ("upstream", "runtime"))
        self.assertEqual(a.gap_id, b.gap_id)

    def test_registry_preserves_unknown_until_requirements_are_satisfied(self):
        registry = ResearchRegistry()
        gap = registry.seed_gap(
            subject="8086:A7A9",
            question="Can macOS accelerate this GPU?",
            reason="hardware identity is known but acceleration is not proven",
            required_evidence_types=("upstream_support", "runtime"),
        )
        source = registry.add_source(
            ResearchSource(SourceType.UPSTREAM_REPOSITORY, "https://example.invalid/gpu-support")
        )
        registry.add_observation(
            ResearchObservation(
                gap.gap_id,
                "implementation support is not established",
                ObservationDisposition.INSUFFICIENT,
                "upstream_support",
                source.source_id,
            )
        )
        self.assertEqual(registry.status_for(gap.gap_id).value, "IN_RESEARCH")

    def test_conflicting_observation_is_explicit(self):
        registry = ResearchRegistry()
        gap = registry.seed_gap(subject="storage", question="Is the path proven?", reason="no accepted evidence")
        source = registry.add_source(ResearchSource(SourceType.REAL_MACHINE_OBSERVATION, "machine://observation/1"))
        registry.add_observation(
            ResearchObservation(
                gap.gap_id, "path failed", ObservationDisposition.CONTRADICTING, "runtime", source.source_id
            )
        )
        self.assertEqual(registry.status_for(gap.gap_id).value, "CONFLICTED")

    def test_sufficient_requires_every_requirement(self):
        registry = ResearchRegistry()
        gap = registry.seed_gap(subject="audio", question="Is layout proven?", reason="layout unknown")
        req = registry.add_requirement(
            EvidenceRequirement(gap.gap_id, "runtime", "audio path works", "runtime proof required")
        )
        registry.add_source(ResearchSource(SourceType.REAL_MACHINE_OBSERVATION, "machine://audio"))
        self.assertEqual(registry.status_for(gap.gap_id).value, "OPEN")
        registry.requirements[req.requirement_id] = EvidenceRequirement(
            gap.gap_id, req.evidence_type, req.claim, req.rationale, req.source_scopes, EvidenceRequirementStatus.SATISFIED, req.requirement_id
        )
        self.assertEqual(registry.status_for(gap.gap_id).value, "SUFFICIENT")


if __name__ == "__main__":
    unittest.main()
