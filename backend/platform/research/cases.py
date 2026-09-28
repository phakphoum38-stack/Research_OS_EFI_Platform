from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from backend.platform.contracts import digest
from .models import EvidenceRequirement, ResearchGap


class ResearchCaseState(str, Enum):
    PLANNED = "PLANNED"
    RESEARCHING = "RESEARCHING"
    EVIDENCE_READY = "EVIDENCE_READY"
    CONFLICTED = "CONFLICTED"
    INCONCLUSIVE = "INCONCLUSIVE"
    CLOSED = "CLOSED"


@dataclass(frozen=True)
class ResearchCase:
    case_id: str
    gap_id: str
    subject: str
    question: str
    hypothesis: str
    state: ResearchCaseState = ResearchCaseState.PLANNED
    requirement_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    provenance: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_gap(cls, gap: ResearchGap, hypothesis: str, *, provenance: Mapping[str, Any] | None = None) -> "ResearchCase":
        if not hypothesis.strip():
            raise ValueError("hypothesis is required")
        case_id = "case-" + digest({"gap_id": gap.gap_id, "hypothesis": hypothesis})[:24]
        return cls(
            case_id=case_id,
            gap_id=gap.gap_id,
            subject=gap.subject,
            question=gap.question,
            hypothesis=hypothesis,
            requirement_ids=tuple(r.requirement_id for r in gap.requirements),
            provenance=dict(provenance or {}),
        )

    def begin(self) -> "ResearchCase":
        return self._with_state(ResearchCaseState.RESEARCHING)

    def record_evidence(self, evidence_id: str) -> "ResearchCase":
        if not evidence_id.strip():
            raise ValueError("evidence_id is required")
        return ResearchCase(
            **{
                **self.to_dict(),
                "state": ResearchCaseState.EVIDENCE_READY,
                "requirement_ids": tuple(self.requirement_ids),
                "evidence_ids": tuple(sorted(set(self.evidence_ids + (evidence_id,)))),
                "provenance": dict(self.provenance),
            }
        )

    def resolve(self, *, conflicted: bool = False, conclusive: bool = True) -> "ResearchCase":
        if conflicted:
            state = ResearchCaseState.CONFLICTED
        elif conclusive:
            state = ResearchCaseState.EVIDENCE_READY
        else:
            state = ResearchCaseState.INCONCLUSIVE
        return self._with_state(state)

    def close(self) -> "ResearchCase":
        return self._with_state(ResearchCaseState.CLOSED)

    def _with_state(self, state: ResearchCaseState) -> "ResearchCase":
        return ResearchCase(
            self.case_id, self.gap_id, self.subject, self.question, self.hypothesis,
            state, self.requirement_ids, self.evidence_ids, dict(self.provenance)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "gap_id": self.gap_id,
            "subject": self.subject,
            "question": self.question,
            "hypothesis": self.hypothesis,
            "state": self.state.value,
            "requirement_ids": list(self.requirement_ids),
            "evidence_ids": list(self.evidence_ids),
            "provenance": dict(self.provenance),
        }


@dataclass
class ResearchCaseEngine:
    cases: dict[str, ResearchCase] = field(default_factory=dict)

    def create(self, gap: ResearchGap, hypothesis: str, *, provenance: Mapping[str, Any] | None = None) -> ResearchCase:
        case = ResearchCase.from_gap(gap, hypothesis, provenance=provenance)
        existing = self.cases.get(case.case_id)
        if existing is not None and existing != case:
            raise ValueError(f"conflicting research case: {case.case_id}")
        self.cases[case.case_id] = case
        return case

    def put(self, case: ResearchCase) -> ResearchCase:
        self.cases[case.case_id] = case
        return case

    def get(self, case_id: str) -> ResearchCase:
        return self.cases[case_id]
