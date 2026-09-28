from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

from backend.platform.contracts import digest


class SourceType(str, Enum):
    VENDOR_DOCUMENTATION = "vendor_documentation"
    UPSTREAM_REPOSITORY = "upstream_repository"
    HARDWARE_DATABASE = "hardware_database"
    TECHNICAL_DOCUMENTATION = "technical_documentation"
    COMMUNITY_OBSERVATION = "community_observation"
    REAL_MACHINE_OBSERVATION = "real_machine_observation"
    OTHER = "other"


@dataclass(frozen=True)
class ResearchSource:
    source_type: SourceType
    locator: str
    title: str = ""
    authority_scope: str = ""
    retrieved_at: str = ""
    source_sha: str = ""
    source_id: str = ""

    def __post_init__(self) -> None:
        if not self.locator.strip():
            raise ValueError("locator is required")
        if not self.source_id:
            body = {
                "source_type": self.source_type.value,
                "locator": self.locator,
                "title": self.title,
                "authority_scope": self.authority_scope,
                "retrieved_at": self.retrieved_at,
                "source_sha": self.source_sha,
            }
            object.__setattr__(self, "source_id", "source-" + digest(body)[:24])

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["source_type"] = self.source_type.value
        return data
