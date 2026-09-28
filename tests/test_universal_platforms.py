import unittest

from backend.platform.universal.capabilities import (
    CapabilityKey,
    CapabilityMatrix,
    CapabilityObservation,
    CapabilityState,
)
from backend.platform.universal.platforms import PlatformId, host_platform, platform_report


class UniversalPlatformTests(unittest.TestCase):
    def test_registry_contains_independent_os_domains(self):
        report = platform_report()
        ids = {item["platform_id"] for item in report["platforms"]}
        self.assertIn("windows", ids)
        self.assertIn("linux", ids)
        self.assertIn("macos", ids)

    def test_capability_observation_keeps_platform_boundary(self):
        matrix = CapabilityMatrix()
        matrix.add(
            CapabilityObservation(
                PlatformId.MACOS,
                CapabilityKey("gpu", "acceleration"),
                CapabilityState.OBSERVED,
                "macOS observation",
            )
        )
        self.assertEqual(len(matrix.for_platform(PlatformId.MACOS)), 1)
        self.assertEqual(len(matrix.for_platform(PlatformId.WINDOWS)), 0)

    def test_host_platform_is_known(self):
        self.assertIn(host_platform(), set(PlatformId))


if __name__ == "__main__":
    unittest.main()
