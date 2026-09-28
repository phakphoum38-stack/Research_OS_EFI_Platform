from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from backend.platform.research.evidence import EvidenceAssessment
from backend.platform.research.machine_evidence import MachineEvidenceRecord


@dataclass(frozen=True)
class CompatibilityDecisionV2:
    subject: str
    level: str
    evidence_id: str
    case_id: str
    hardware_identity_sha: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "level": self.level,
            "evidence_id": self.evidence_id,
            "case_id": self.case_id,
            "hardware_identity_sha": self.hardware_identity_sha,
            "reason": self.reason,
        }


def decide_from_machine_evidence(
    *,
    subject: str,
    assessment: EvidenceAssessment,
    machine: MachineEvidenceRecord,
) -> CompatibilityDecisionV2 | None:
    """Return a decision only for explicit real-machine macOS proof.

    The function emits a decision object and never mutates a compatibility profile.
    """
    if assessment.state != "SUPPORTED":
        return None
    if not machine.physical_machine:
        return None
    if machine.platform.strip().lower() != "macos":
        return None
    if machine.runtime_result != "PASSED":
        return None
    if not assessment.supporting or machine.evidence_id not in assessment.supporting:
        return None
    return CompatibilityDecisionV2(
        subject=subject,
        level="MACOS_PROVEN",
        evidence_id=machine.evidence_id,
        case_id=machine.case_id,
        hardware_identity_sha=machine.hardware_identity_sha,
        reason="explicit real-machine macOS runtime evidence satisfied the research assessment",
    )
