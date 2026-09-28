from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class ResearchObservation:
    observation_id: str
    gap_id: str
    source_id: str
    statement: str
    supports: bool | None
    evidence_type: str
    evidence_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.observation_id or not self.gap_id or not self.source_id or not self.statement:
            raise ValueError("observation identity and statement are required")
        if not self.evidence_type:
            raise ValueError("evidence_type is required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "gap_id": self.gap_id,
            "source_id": self.source_id,
            "statement": self.statement,
            "supports": self.supports,
            "evidence_type": self.evidence_type,
            "evidence_id": self.evidence_id,
            "metadata": dict(self.metadata),
        }
