from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from backend.platform.contracts import digest


@dataclass(frozen=True)
class Provenance:
    source_id: str
    source_sha: str = ""
    retrieved_at: str = ""
    locator: str = ""
    note: str = ""

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("source_id is required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_sha": self.source_sha,
            "retrieved_at": self.retrieved_at,
            "locator": self.locator,
            "note": self.note,
        }

    def fingerprint(self) -> str:
        return digest(self.to_dict())


def merge_provenance(*items: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    """Deduplicate provenance records without deciding which source is authoritative."""
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for item in items:
        value = dict(item)
        key = digest(value)
        if key not in seen:
            seen.add(key)
            result.append(value)
    return tuple(result)
