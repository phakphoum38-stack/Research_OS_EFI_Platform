from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping


class EvidenceLevel(str, Enum):
    UNKNOWN = "UNKNOWN"
    OBSERVED = "OBSERVED"
    FIRMWARE_PROVEN = "FIRMWARE_PROVEN"
    OS_PROVEN = "OS_PROVEN"
    MACOS_PROVEN = "MACOS_PROVEN"
    RUNTIME_PROVEN = "RUNTIME_PROVEN"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class Evidence:
    subject: str
    level: EvidenceLevel
    source: str
    value: Any = None
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["level"] = self.level.value
        return data


@dataclass
class EvidenceManifest:
    machine: str
    generated_by: str = "hackintosh-ai-platform"
    schema_version: str = "1.0"
    evidence: list[Evidence] = field(default_factory=list)

    def add(self, evidence: Evidence) -> None:
        self.evidence.append(evidence)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generated_by": self.generated_by,
            "machine": self.machine,
            "evidence": [item.to_dict() for item in self.evidence],
        }

    @classmethod
    def from_profile(cls, profile: Mapping[str, Any]) -> "EvidenceManifest":
        manifest = cls(machine=str(profile.get("machine", "unknown")))
        cpu = profile.get("cpu", {})
        if cpu.get("model"):
            level = EvidenceLevel.OS_PROVEN if cpu.get("status") == "proven" else EvidenceLevel.OBSERVED
            manifest.add(Evidence("cpu", level, "hardware profile", cpu["model"]))
        gpu = profile.get("gpu", {})
        if gpu.get("pci_id"):
            level = EvidenceLevel.MACOS_PROVEN if gpu.get("acceleration_status") == "proven" else EvidenceLevel.OBSERVED
            manifest.add(Evidence("gpu", level, "hardware profile", gpu["pci_id"], gpu.get("name", "")))
        storage = profile.get("storage", {})
        vmd = storage.get("vmd", {})
        if vmd.get("ids"):
            level = EvidenceLevel.MACOS_PROVEN if vmd.get("status") == "proven" else EvidenceLevel.OBSERVED
            manifest.add(Evidence("vmd", level, "hardware profile", vmd["ids"]))
        return manifest
