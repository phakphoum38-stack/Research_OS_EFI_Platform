from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


VALID_STATES = {"UNKNOWN", "RESEARCH", "SUPPORTED", "PROVEN", "CONFLICTED", "INSUFFICIENT"}


@dataclass(frozen=True)
class EvidenceRequirement:
    requirement_id: str
    subject: str
    claim: str
    evidence_types: tuple[str, ...]
    minimum_observations: int = 1
    rationale: str = ""

    def __post_init__(self) -> None:
        if not self.requirement_id or not self.subject or not self.claim:
            raise ValueError("requirement_id, subject, and claim are required")
        if not self.evidence_types:
            raise ValueError("at least one evidence type is required")
        if self.minimum_observations < 1:
            raise ValueError("minimum_observations must be >= 1")

    def to_dict(self) -> dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "subject": self.subject,
            "claim": self.claim,
            "evidence_types": list(self.evidence_types),
            "minimum_observations": self.minimum_observations,
            "rationale": self.rationale,
        }


@dataclass(frozen=True)
class ResearchGap:
    gap_id: str
    subject: str
    question: str
    state: str = "RESEARCH"
    known_facts: tuple[str, ...] = ()
    requirements: tuple[EvidenceRequirement, ...] = ()
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.state not in VALID_STATES:
            raise ValueError(f"unsupported research state: {self.state}")
        if not self.gap_id or not self.subject or not self.question:
            raise ValueError("gap_id, subject, and question are required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "gap_id": self.gap_id,
            "subject": self.subject,
            "question": self.question,
            "state": self.state,
            "known_facts": list(self.known_facts),
            "requirements": [r.to_dict() for r in self.requirements],
            "provenance": dict(self.provenance),
        }
