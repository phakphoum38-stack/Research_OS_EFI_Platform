from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from backend.platform.contracts import digest
from backend.platform.universal.identity import hardware_identity_sha
from backend.platform.universal.models import HardwareSnapshot
from .observations import ResearchObservation


@dataclass(frozen=True)
class MachineEvidenceRecord:
    case_id: str
    platform: str
    product_identity: Mapping[str, Any]
    hardware_identity_sha: str
    evidence_id: str
    physical_machine: bool
    runtime_result: str
    provenance: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not self.case_id or not self.platform or not self.evidence_id:
            raise ValueError("case_id, platform and evidence_id are required")
        if not self.hardware_identity_sha:
            raise ValueError("hardware_identity_sha is required")
        if self.physical_machine and self.runtime_result not in {"PASSED", "FAILED", "INCONCLUSIVE", "ABORTED"}:
            raise ValueError("invalid runtime result")

    def to_observation(
        self,
        *,
        gap_id: str,
        statement: str,
        supports: bool | None,
        evidence_type: str = "real_machine_runtime",
    ) -> ResearchObservation:
        if not gap_id or not statement:
            raise ValueError("gap_id and statement are required")
        observation_id = "machine-obs-" + digest({
            "evidence_id": self.evidence_id,
            "gap_id": gap_id,
            "statement": statement,
        })[:24]
        return ResearchObservation(
            observation_id=observation_id,
            gap_id=gap_id,
            source_id=str(self.provenance.get("source_id", self.evidence_id)),
            statement=statement,
            supports=supports,
            evidence_type=evidence_type,
            evidence_id=self.evidence_id,
            metadata={
                "platform": self.platform,
                "physical_machine": self.physical_machine,
                "runtime_result": self.runtime_result,
                "hardware_identity_sha": self.hardware_identity_sha,
            },
        )


def record_machine_evidence(
    snapshot: HardwareSnapshot,
    *,
    case_id: str,
    evidence_id: str,
    runtime_result: str,
    physical_machine: bool,
    provenance: Mapping[str, Any] | None = None,
) -> MachineEvidenceRecord:
    """Bind runtime evidence to the exact observed hardware identity.

    This records identity/provenance only; it never changes compatibility state.
    """
    return MachineEvidenceRecord(
        case_id=case_id,
        platform=snapshot.platform,
        product_identity=snapshot.product.to_dict(),
        hardware_identity_sha=hardware_identity_sha(snapshot),
        evidence_id=evidence_id,
        physical_machine=physical_machine,
        runtime_result=runtime_result,
        provenance=dict(provenance or {}),
    )
