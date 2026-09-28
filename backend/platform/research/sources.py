from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class ResearchSource:
    source_id: str
    source_type: str
    locator: str
    retrieved_at: str
    source_sha: str | None = None
    authority_scope: str = "research"
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.source_id or not self.source_type or not self.locator:
            raise ValueError("source_id, source_type, and locator are required")
        if self.source_sha is not None and len(self.source_sha) != 64:
            raise ValueError("source_sha must be a 64-character SHA-256 hex digest")
        if self.source_sha is not None:
            int(self.source_sha, 16)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_type": self.source_type,
            "locator": self.locator,
            "retrieved_at": self.retrieved_at,
            "source_sha": self.source_sha,
            "authority_scope": self.authority_scope,
            "provenance": dict(self.provenance),
        }


@dataclass
class ResearchSourceRegistry:
    _items: dict[str, ResearchSource]

    def __init__(self, items=()) -> None:
        self._items = {}
        for item in items:
            self.add(item)

    def add(self, source: ResearchSource) -> None:
        if source.source_id in self._items:
            raise ValueError(f"duplicate research source: {source.source_id}")
        self._items[source.source_id] = source

    def get(self, source_id: str) -> ResearchSource:
        try:
            return self._items[source_id]
        except KeyError as exc:
            raise KeyError(f"unknown research source: {source_id}") from exc

    def list(self) -> tuple[ResearchSource, ...]:
        return tuple(self._items[key] for key in sorted(self._items))

    def to_dict(self) -> list[dict[str, Any]]:
        return [s.to_dict() for s in self.list()]
