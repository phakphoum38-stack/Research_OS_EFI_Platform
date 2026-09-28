"""Research-gap and evidence-discovery foundation for Research OS EFI Platform."""

from .gaps import ResearchGap, ResearchGapStatus
from .observations import ResearchObservation, ObservationDisposition
from .registry import ResearchRegistry
from .requirements import EvidenceRequirement
from .sources import ResearchSource, SourceType

__all__ = [
    "ResearchGap",
    "ResearchGapStatus",
    "ResearchObservation",
    "ObservationDisposition",
    "ResearchRegistry",
    "EvidenceRequirement",
    "ResearchSource",
    "SourceType",
]
