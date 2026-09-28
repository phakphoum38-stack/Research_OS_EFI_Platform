from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Mapping

from backend.platform.contracts import digest


class ObservationDisposition(str, Enum):
    SUPPORTING = "SUPPORTING"
    CONTRADICTING = "CONTRADICTING"
    INSUFFICIENT = "INSUFFICIENT"


@dataclass(frozen=True)
class ResearchObservation:
    gap_id: str
    statement: str
    disposition: ObservationDisposition
    evidence_type: str
    source_id: str
    payload: Mapping[str, Any] | None = None
    observation_id: str = ""

    def __post_init__(self) -> None:
        for name, value in (
            ("gap_id", self.gap_id),
            ("statement", self.statement),
            ("evidence_type", self.evidence_type),
            ("source_id", self.source_id),
        ):
            if not str(value).strip():
                raise ValueError(f"{name} is required")
        if not self.observation_id:
            body = {
                "gap_id": self.gap_id,
                "statement": self.statement,
                "disposition": self.disposition.value,
                "evidence_type": self.evidence_type,
                "source_id": self.source_id,
                "payload": dict(self.payload or {}),
            }
            object.__setattr__(self, "observation_id", "obs-" + digest(body)[:24])

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["disposition"] = self.disposition.value
        data["payload"] = dict(self.payload or {})
        return data
