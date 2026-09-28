import tempfile
import unittest
from pathlib import Path

from backend.platform.universal.runtime.engine import RuntimeSession
from backend.platform.universal.runtime.evidence import (
    envelope_for_session,
    load_and_verify_session,
    write_session_evidence,
)


class UniversalRuntimeEvidenceTests(unittest.TestCase):
    def test_runtime_session_evidence_requires_case_and_hardware_identity(self):
        session = RuntimeSession("windows")
        with self.assertRaises(ValueError):
            envelope_for_session(session, case_id="case")
        with self.assertRaises(ValueError):
            envelope_for_session(
                session,
                case_id="case",
                hardware_identity_sha="",
            )

    def test_runtime_session_evidence_round_trips(self):
        session = RuntimeSession("windows")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime-session.json"
            write_session_evidence(
                session,
                str(path),
                source_sha="source",
                case_id="case-1",
                hardware_identity_sha="hardware-1",
            )
            loaded = load_and_verify_session(str(path))
        self.assertEqual(loaded["kind"], "runtime-session")
        self.assertEqual(loaded["payload"]["case_id"], "case-1")
        self.assertEqual(loaded["payload"]["hardware_identity_sha"], "hardware-1")


if __name__ == "__main__":
    unittest.main()
