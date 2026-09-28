from __future__ import annotations

from dataclasses import dataclass

from .gaps import ResearchGapRegistry
from .models import ResearchGap
from .sources import ResearchSourceRegistry


@dataclass
class ResearchRegistry:
    gaps: ResearchGapRegistry
    sources: ResearchSourceRegistry

    def __init__(self, gaps=(), sources=()) -> None:
        self.gaps = ResearchGapRegistry(gaps)
        self.sources = ResearchSourceRegistry(sources)

    def register_gap(self, gap: ResearchGap) -> None:
        self.gaps.add(gap)

    def to_dict(self) -> dict:
        return {"gaps": self.gaps.to_dict(), "sources": self.sources.to_dict()}
