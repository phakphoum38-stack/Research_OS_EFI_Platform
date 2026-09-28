from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .candidate import generate_candidate
from .contracts import EvidenceEnvelope
from .opencore import validate_opencore
from .preflight import build_preflight
from .research_case import ResearchCase
from .orchestrator import build_plan


def fingerprint_tree(root: str) -> str:
    """Return a deterministic digest of candidate files, excluding the packet."""
    base = Path(root)
    digest = hashlib.sha256()
    for path in sorted(p for p in base.rglob("*") if p.is_file() and p.name != "evidence-packet.json"):
        rel = path.relative_to(base).as_posix().encode()
        digest.update(rel)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def build_evidence_packet(
    profile: Mapping[str, Any],
    output: str,
    source_sha: str,
    hypothesis: str,
    case_id: str = "x1504va-research",
) -> dict[str, Any]:
    """Run candidate -> validation -> preflight as one evidence-first pipeline.

    The pipeline can prepare and inspect an artifact, but never authorizes or
    performs a hardware/firmware operation.
    """
    root = Path(output)
    root.mkdir(parents=True, exist_ok=True)
    candidate = generate_candidate(profile, str(root))
    candidate_sha = fingerprint_tree(str(root))
    experiment = {
        "hypothesis": hypothesis,
        "candidate_sha": candidate_sha,
        "status": "PLANNED",
    }
    opencore = validate_opencore(str(root))
    preflight = build_preflight(profile, str(root), experiment)
    case = ResearchCase.from_profile(
        case_id,
        source_sha,
        str(profile.get("machine", "unknown")),
        hypothesis,
        profile,
        [],
    )
    plan = build_plan(case)
    packet = {
        "schema_version": "1.0",
        "status": preflight["status"],
        "source_sha": source_sha,
        "candidate_sha": candidate_sha,
        "candidate": candidate,
        "opencore_validation": opencore,
        "preflight": preflight,
        "research_plan": plan.to_dict(),
        "safety": {
            "mutation_performed": False,
            "hardware_mutation_authorized": False,
            "human_boot_boundary": True,
        },
    }
    envelope = EvidenceEnvelope.create(
        source_sha,
        "efi-evidence-packet",
        packet["status"],
        packet,
        {
            "pipeline": "candidate-validation-preflight",
            "candidate_sha": candidate_sha,
        },
    )
    packet["evidence_envelope"] = envelope.to_dict()
    return packet


def write_evidence_packet(packet: Mapping[str, Any], output: str) -> None:
    Path(output).write_text(
        json.dumps(dict(packet), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
