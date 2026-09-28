from __future__ import annotations

from .models import EvidenceRequirement


def requirement_for_hardware_claim(
    *, requirement_id: str, subject: str, claim: str, evidence_types: tuple[str, ...], rationale: str = ""
) -> EvidenceRequirement:
    """Create an explicit proof requirement; no source is treated as authoritative."""
    return EvidenceRequirement(
        requirement_id=requirement_id,
        subject=subject,
        claim=claim,
        evidence_types=evidence_types,
        rationale=rationale,
    )
