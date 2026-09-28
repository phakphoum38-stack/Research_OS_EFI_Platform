from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import ResearchGap
from .observations import ResearchObservation


@dataclass(frozen=True)
class EvidenceAssessment:
    gap_id: str
    state: str
    supporting: tuple[str, ...]
    contradicting: tuple[str, ...]
    unresolved: tuple[str, ...]
    reason: str

    def to_dict(self) -> dict:
        return {
            "gap_id": self.gap_id,
            "state": self.state,
            "supporting": list(self.supporting),
            "contradicting": list(self.contradicting),
            "unresolved": list(self.unresolved),
            "reason": self.reason,
        }


def assess_gap(gap: ResearchGap, observations: Iterable[ResearchObservation]) -> EvidenceAssessment:
    """Assess evidence direction without promoting a claim to PROVEN automatically."""
    relevant = tuple(o for o in observations if o.gap_id == gap.gap_id)
    supporting = tuple(o.observation_id for o in relevant if o.supports is True)
    contradicting = tuple(o.observation_id for o in relevant if o.supports is False)
    unresolved = tuple(o.observation_id for o in relevant if o.supports is None)

    if supporting and contradicting:
        state, reason = "CONFLICTED", "supporting and contradicting observations coexist"
    elif len(supporting) >= sum(r.minimum_observations for r in gap.requirements) and supporting:
        state, reason = "SUPPORTED", "minimum supporting observations are present"
    elif relevant:
        state, reason = "INSUFFICIENT", "observations exist but do not satisfy the proof requirement"
    else:
        state, reason = "RESEARCH", "no observations have been ingested for this gap"

    return EvidenceAssessment(gap.gap_id, state, supporting, contradicting, unresolved, reason)
