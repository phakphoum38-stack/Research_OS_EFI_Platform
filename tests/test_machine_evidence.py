import unittest

from backend.platform.research.machine_evidence import record_machine_evidence
from backend.platform.universal.models import HardwareSnapshot, ProductIdentity


class MachineEvidenceTests(unittest.TestCase):
    def test_machine_evidence_binds_exact_hardware_identity(self):
        snapshot = HardwareSnapshot(
            platform="windows",
            product=ProductIdentity(manufacturer="ASUS", product="X1504VA", board="X1504VA"),
        )
        record = record_machine_evidence(
            snapshot,
            case_id="case-1",
            evidence_id="evidence-1",
            runtime_result="PASSED",
            physical_machine=True,
            provenance={"source_id": "machine-1"},
        )
        self.assertEqual(len(record.hardware_identity_sha), 64)
        observation = record.to_observation(
            gap_id="gap-1",
            statement="runtime observation captured",
            supports=None,
        )
        self.assertEqual(observation.metadata["hardware_identity_sha"], record.hardware_identity_sha)
        self.assertIsNone(observation.supports)

    def test_physical_result_is_validated(self):
        snapshot = HardwareSnapshot(platform="linux", product=ProductIdentity(product="fixture"))
        with self.assertRaises(ValueError):
            record_machine_evidence(
                snapshot,
                case_id="case-1",
                evidence_id="evidence-1",
                runtime_result="BOGUS",
                physical_machine=True,
            )


if __name__ == "__main__":
    unittest.main()
