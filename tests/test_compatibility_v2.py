import unittest

from backend.platform.compatibility_v2 import decide_from_machine_evidence
from backend.platform.research.evidence import EvidenceAssessment
from backend.platform.research.machine_evidence import MachineEvidenceRecord


class CompatibilityV2Tests(unittest.TestCase):
    def machine(self, *, physical=True, platform="macos", result="PASSED"):
        return MachineEvidenceRecord(
            "case-1", platform, {"product": "fixture"}, "a" * 64, "evidence-1",
            physical, result, {"source_id": "source-1"},
        )

    def assessment(self, state="SUPPORTED", supporting=("evidence-1",)):
        return EvidenceAssessment("gap-1", state, supporting, (), (), "fixture")

    def test_only_explicit_real_machine_macos_evidence_can_emit_proven(self):
        decision = decide_from_machine_evidence(
            subject="8086:A7A9",
            assessment=self.assessment(),
            machine=self.machine(),
        )
        self.assertEqual(decision.level, "MACOS_PROVEN")

    def test_synthetic_or_incomplete_evidence_never_emits_decision(self):
        for machine in (
            self.machine(physical=False),
            self.machine(platform="linux"),
            self.machine(result="INCONCLUSIVE"),
        ):
            self.assertIsNone(decide_from_machine_evidence(
                subject="8086:A7A9",
                assessment=self.assessment(),
                machine=machine,
            ))
        self.assertIsNone(decide_from_machine_evidence(
            subject="8086:A7A9",
            assessment=self.assessment("INSUFFICIENT"),
            machine=self.machine(),
        ))


if __name__ == "__main__":
    unittest.main()
