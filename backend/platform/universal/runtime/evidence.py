from __future__ import annotations

import json
from pathlib import Path

from ..contracts import EvidenceEnvelope, verify_envelope
from .engine import RuntimeSession


def envelope_for_session(
    session: RuntimeSession,
    *,
    source_sha: str = "",
    case_id: str = "",
    hardware_identity_sha: str = "",
) -> EvidenceEnvelope:
    if not case_id:
        raise ValueError("case_id is required")
    if not hardware_identity_sha:
        raise ValueError("hardware_identity_sha is required")
    payload = session.to_dict()
    payload["case_id"] = case_id
    payload["hardware_identity_sha"] = hardware_identity_sha
    result = "PASSED" if session.results and all(
        item.returncode == 0 for item in session.results
    ) else "FAILED"
    return EvidenceEnvelope.create(
        source_sha or "UNPINNED_SOURCE",
        "runtime-session",
        result,
        payload,
        {
            "platform": session.platform,
            "case_id": case_id,
            "hardware_identity_sha": hardware_identity_sha,
            "execution_boundary": "local-os-runtime",
        },
    )


def write_session_evidence(
    session: RuntimeSession,
    output: str,
    *,
    source_sha: str = "",
    case_id: str = "",
    hardware_identity_sha: str = "",
) -> None:
    envelope = envelope_for_session(
        session,
        source_sha=source_sha,
        case_id=case_id,
        hardware_identity_sha=hardware_identity_sha,
    )
    Path(output).write_text(
        json.dumps(envelope.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def load_and_verify_session(path: str) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not verify_envelope(value):
        raise ValueError("invalid runtime-session evidence envelope")
    if value.get("kind") != "runtime-session":
        raise ValueError("unexpected runtime-session evidence kind")
    return value
