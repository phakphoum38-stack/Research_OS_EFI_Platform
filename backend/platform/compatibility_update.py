from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .compatibility_learning import CompatibilityDecision


@dataclass(frozen=True)
class CompatibilityUpdateProposal:
    component: str
    current_value: str
    proposed_value: str
    current_level: str
    proposed_level: str
    evidence_id: str
    case_id: str
    source_sha: str
    candidate_sha: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "component": self.component,
            "current_value": self.current_value,
            "proposed_value": self.proposed_value,
            "current_level": self.current_level,
            "proposed_level": self.proposed_level,
            "evidence_id": self.evidence_id,
            "case_id": self.case_id,
            "source_sha": self.source_sha,
            "candidate_sha": self.candidate_sha,
            "reason": self.reason,
        }


def build_proposal(
    decision: CompatibilityDecision,
    *,
    current_value: str,
    current_level: str,
) -> CompatibilityUpdateProposal:
    if not decision.evidence_id:
        raise ValueError("evidence_id is required")
    if not decision.case_id:
        raise ValueError("case_id is required")
    if not decision.source_sha:
        raise ValueError("source_sha is required")
    if not decision.candidate_sha:
        raise ValueError("candidate_sha is required")
    if not current_value:
        raise ValueError("current_value is required")
    if not current_level:
        raise ValueError("current_level is required")
    return CompatibilityUpdateProposal(
        component=decision.component,
        current_value=current_value,
        proposed_value=decision.value,
        current_level=current_level,
        proposed_level=decision.level.value,
        evidence_id=decision.evidence_id,
        case_id=decision.case_id,
        source_sha=decision.source_sha,
        candidate_sha=decision.candidate_sha,
        reason=decision.reason,
    )


def verify_proposal(proposal: CompatibilityUpdateProposal) -> bool:
    values = (
        proposal.component,
        proposal.current_value,
        proposal.proposed_value,
        proposal.current_level,
        proposal.proposed_level,
        proposal.evidence_id,
        proposal.case_id,
        proposal.source_sha,
        proposal.candidate_sha,
        proposal.reason,
    )
    return all(isinstance(value, str) and value.strip() for value in values)
