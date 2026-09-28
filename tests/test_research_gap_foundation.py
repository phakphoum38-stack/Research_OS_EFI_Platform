import unittest

from backend.platform.research.gaps import ResearchGapRegistry
from backend.platform.research.models import ResearchGap
from backend.platform.research.observations import ResearchObservation
from backend.platform.research.provenance import source_fingerprint
from backend.platform.research.requirements import requirement_for_hardware_claim
from backend.platform.research.sources import ResearchSource, ResearchSourceRegistry


class ResearchGapFoundationTests(unittest.TestCase):
    def test_unknown_is_explicitly_modelled_as_research_gap(self):
        req = requirement_for_hardware_claim(
            requirement_id="gpu-a7a9-macos-accel",
            subject="8086:A7A9",
            claim="macOS graphics acceleration",
            evidence_types=("upstream", "runtime"),
        )
        gap = ResearchGap(
            gap_id="x1504va-gpu-a7a9",
            subject="8086:A7A9",
            question="Can macOS obtain graphics acceleration?",
            known_facts=("PCI identity observed", "firmware GFX0 topology observed"),
            requirements=(req,),
        )
        registry = ResearchGapRegistry([gap])
        value = registry.get("x1504va-gpu-a7a9").to_dict()
        self.assertEqual(value["state"], "RESEARCH")
        self.assertEqual(value["requirements"][0]["claim"], "macOS graphics acceleration")

    def test_source_is_not_truth_and_is_provenance_anchored(self):
        source = ResearchSource(
            source_id="src-1",
            source_type="technical-repository",
            locator="example://source",
            retrieved_at="2026-09-28T00:00:00Z",
        )
        registry = ResearchSourceRegistry([source])
        self.assertEqual(registry.get("src-1").authority_scope, "research")
        self.assertEqual(len(source_fingerprint(source_id="src-1", locator="example://source", source_sha=None)), 64)

    def test_observation_keeps_support_direction_and_source(self):
        observation = ResearchObservation(
            observation_id="obs-1",
            gap_id="gap-1",
            source_id="src-1",
            statement="implementation mentions device family",
            supports=None,
            evidence_type="upstream",
        )
        self.assertIsNone(observation.supports)
        self.assertEqual(observation.source_id, "src-1")


if __name__ == "__main__":
    unittest.main()
