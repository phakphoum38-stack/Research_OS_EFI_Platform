import json
import unittest

from backend.builder.compatibility import evaluate_hardware


class CompatibilityTests(unittest.TestCase):
    def test_x1504va_is_conservatively_blocked(self):
        with open("hardware/x1504va.json", encoding="utf-8") as handle:
            profile = json.load(handle)

        result = evaluate_hardware(profile)

        self.assertEqual(result.status, "BLOCKED")
        self.assertTrue(any("A7A9" in item for item in result.blockers))
        self.assertTrue(any("VMD" in item for item in result.blockers))
        self.assertTrue(any("MT7902" in item for item in result.warnings))
        self.assertIn("Realtek ALC256 codec family", result.proven)


if __name__ == "__main__":
    unittest.main()
