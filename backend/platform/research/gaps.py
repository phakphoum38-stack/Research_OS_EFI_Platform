from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Mapping

from backend.platform.contracts import digest


class ResearchGapStatus(str, Enum):
    OPEN = "OPEN"
    IN_RESEARCH = "IN_RESEARCH"
    SUFFICIENT = "SUFFICIENT"
    CONFLICTED = "CONFLICTED"
    CLOSED = "CLOSED"


@dataclass(frozen=True)
class ResearchGap:
    subject: str
    question: str
    reason: str
    required_evidence_types: tuple[str, ...] = ()
    context: Mapping[str, Any] | None = None
    gap_id: str = ""

    def __post_init__(self) -> None:
        if not self.subject.strip():
            raise ValueError("subject is required")
        if not self.question.strip():
            raise ValueError("question is required")
        if not self.reason.strip():
            raise ValueError("reason is required")
        types = tuple(sorted(set(t.strip() for t in self.required_evidence_types if t.strip())))
        object.__setattr__(self, "required_evidence_types", types)
        if not self.gap_id:
            body = {
                "subject": self.subject,
                "question": self.question,
                "reason": self.reason,
                "required_evidence_types": types,
                "context": dict(self.context or {}),
            }
            object.__setattr__(self, "gap_id", "gap-" + digest(body)[:24])

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["required_evidence_types"] = list(self.required_evidence_types)
        data["context"] = dict(self.context or {})
        return data
