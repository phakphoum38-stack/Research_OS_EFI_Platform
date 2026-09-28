from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .platforms import PlatformId, normalize_platform


class CapabilityState(str, Enum):
    UNKNOWN = "UNKNOWN"
    OBSERVED = "OBSERVED"
    PROVEN = "PROVEN"
    BLOCKED = "BLOCKED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True)
class CapabilityKey:
    component: str
    capability: str

    def to_dict(self) -> dict[str, str]:
        return {
            "component": self.component,
            "capability": self.capability,
        }


@dataclass(frozen=True)
class CapabilityObservation:
    platform: PlatformId
    key: CapabilityKey
    state: CapabilityState
    statement: str
    evidence_id: str = ""
    source_sha: str = ""
    runtime_version: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "platform": self.platform.value,
            "key": self.key.to_dict(),
            "state": self.state.value,
            "statement": self.statement,
            "evidence_id": self.evidence_id,
            "source_sha": self.source_sha,
            "runtime_version": self.runtime_version,
            "metadata": dict(self.metadata),
        }


@dataclass
class CapabilityMatrix:
    observations: list[CapabilityObservation] = field(default_factory=list)

    def add(self, observation: CapabilityObservation) -> None:
        if not isinstance(observation.platform, PlatformId):
            raise ValueError("capability observation platform must be a PlatformId")
        self.observations.append(observation)

    def for_platform(self, platform: str | PlatformId) -> list[CapabilityObservation]:
        target = normalize_platform(platform)
        return [item for item in self.observations if item.platform == target]

    def for_component(
        self, platform: str | PlatformId, component: str
    ) -> list[CapabilityObservation]:
        target = normalize_platform(platform)
        return [
            item
            for item in self.observations
            if item.platform == target and item.key.component == component
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "observations": [item.to_dict() for item in self.observations],
        }