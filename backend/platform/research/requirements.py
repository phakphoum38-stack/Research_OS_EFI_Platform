from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Mapping

from backend.platform.contracts import digest


class EvidenceRequirementStatus(str, Enum):
    NEEDED = "NEEDED"
    SATISFIED = "SATISFIED"
    CONFLICTED = "CONFLICTED"


@dataclass(frozen=True)
class EvidenceRequirement:
    gap_id: str
    evidence_type: str
    claim: str
    rationale: str
    source_scopes: tuple[str, ...] = ()
    status: EvidenceRequirementStatus = EvidenceRequirementStatus.NEEDED
    requirement_id: str = ""

    def __post_init__(self) -> None:
        for name, value in (("gap_id", self.gap_id), ("evidence_type", self.evidence_type), ("claim", self.claim), ("rationale", self.rationale)):
            if not str(value).strip():
                raise ValueError(f"{name} is required")
        scopes = tuple(sorted(set(s.strip() for s in self.source_scopes if s.strip())))
        object.__setattr__(self, "source_scopes", scopes)
        if not self.requirement_id:
            body = {
                "gap_id": self.gap_id,
                "evidence_type": self.evidence_type,
                "claim": self.claim,
                "rationale": self.rationale,
                "source_scopes": scopes,
            }
            object.__setattr__(self, "requirement_id", "req-" + digest(body)[:24])

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["source_scopes"] = list(self.source_scopes)
        return data
