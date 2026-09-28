from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import ResearchGap


@dataclass
class ResearchGapRegistry:
    _items: dict[str, ResearchGap]

    def __init__(self, items: Iterable[ResearchGap] = ()) -> None:
        self._items = {}
        for item in items:
            self.add(item)

    def add(self, gap: ResearchGap) -> None:
        if gap.gap_id in self._items:
            raise ValueError(f"duplicate research gap: {gap.gap_id}")
        self._items[gap.gap_id] = gap

    def get(self, gap_id: str) -> ResearchGap:
        try:
            return self._items[gap_id]
        except KeyError as exc:
            raise KeyError(f"unknown research gap: {gap_id}") from exc

    def list(self) -> tuple[ResearchGap, ...]:
        return tuple(self._items[key] for key in sorted(self._items))

    def by_subject(self, subject: str) -> tuple[ResearchGap, ...]:
        return tuple(g for g in self.list() if g.subject == subject)

    def to_dict(self) -> list[dict]:
        return [g.to_dict() for g in self.list()]
