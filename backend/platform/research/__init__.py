"""Research-gap and evidence-discovery primitives for Research OS EFI Platform."""

from .gaps import ResearchGap, ResearchGapRegistry
from .requirements import EvidenceRequirement
from .sources import ResearchSource, ResearchSourceRegistry

__all__ = ["ResearchGap", "ResearchGapRegistry", "EvidenceRequirement", "ResearchSource", "ResearchSourceRegistry"]
