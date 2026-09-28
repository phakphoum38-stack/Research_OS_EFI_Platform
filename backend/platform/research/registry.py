from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .gaps import ResearchGap, ResearchGapStatus
from .observations import ObservationDisposition, ResearchObservation
from .requirements import EvidenceRequirement, EvidenceRequirementStatus
from .sources import ResearchSource


@dataclass
class ResearchRegistry:
    gaps: dict[str, ResearchGap] = field(default_factory=dict)
    requirements: dict[str, EvidenceRequirement] = field(default_factory=dict)
    sources: dict[str, ResearchSource] = field(default_factory=dict)
    observations: dict[str, ResearchObservation] = field(default_factory=dict)

    def add_gap(self, gap: ResearchGap) -> ResearchGap:
        self.gaps[gap.gap_id] = gap
        return gap

    def add_requirement(self, requirement: EvidenceRequirement) -> EvidenceRequirement:
        if requirement.gap_id not in self.gaps:
            raise KeyError(f"unknown gap: {requirement.gap_id}")
        self.requirements[requirement.requirement_id] = requirement
        return requirement

    def add_source(self, source: ResearchSource) -> ResearchSource:
        self.sources[source.source_id] = source
        return source

    def add_observation(self, observation: ResearchObservation) -> ResearchObservation:
        if observation.gap_id not in self.gaps:
            raise KeyError(f"unknown gap: {observation.gap_id}")
        if observation.source_id not in self.sources:
            raise KeyError(f"unknown source: {observation.source_id}")
        self.observations[observation.observation_id] = observation
        return observation

    def requirements_for(self, gap_id: str) -> tuple[EvidenceRequirement, ...]:
        return tuple(r for r in self.requirements.values() if r.gap_id == gap_id)

    def observations_for(self, gap_id: str) -> tuple[ResearchObservation, ...]:
        return tuple(o for o in self.observations.values() if o.gap_id == gap_id)

    def status_for(self, gap_id: str) -> ResearchGapStatus:
        if gap_id not in self.gaps:
            raise KeyError(gap_id)
        requirements = self.requirements_for(gap_id)
        observations = self.observations_for(gap_id)
        if any(o.disposition == ObservationDisposition.CONTRADICTING for o in observations):
            return ResearchGapStatus.CONFLICTED
        if requirements and all(r.status == EvidenceRequirementStatus.SATISFIED for r in requirements):
            return ResearchGapStatus.SUFFICIENT
        if observations:
            return ResearchGapStatus.IN_RESEARCH
        return ResearchGapStatus.OPEN

    def open_gaps(self) -> tuple[ResearchGap, ...]:
        return tuple(g for g in self.gaps.values() if self.status_for(g.gap_id) in {ResearchGapStatus.OPEN, ResearchGapStatus.IN_RESEARCH, ResearchGapStatus.CONFLICTED})

    def seed_gap(
        self,
        *,
        subject: str,
        question: str,
        reason: str,
        required_evidence_types: Iterable[str] = (),
        context: dict | None = None,
    ) -> ResearchGap:
        return self.add_gap(
            ResearchGap(
                subject=subject,
                question=question,
                reason=reason,
                required_evidence_types=tuple(required_evidence_types),
                context=context,
            )
        )
