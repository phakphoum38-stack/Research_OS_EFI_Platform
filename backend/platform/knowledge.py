from __future__ import annotations
from dataclasses import dataclass, field
from .evidence import EvidenceLevel

@dataclass(frozen=True)
class CompatibilityFact:
    component: str
    value: str
    level: EvidenceLevel
    source: str
    note: str = ""

@dataclass
class CompatibilityKnowledge:
    facts: list[CompatibilityFact] = field(default_factory=list)
    def add(self,fact): self.facts.append(fact)
    def for_component(self,component): return [f for f in self.facts if f.component==component]
    def unresolved(self): return [f for f in self.facts if f.level in {EvidenceLevel.UNKNOWN,EvidenceLevel.OBSERVED}]
    @classmethod
    def from_profile(cls,profile):
        book=cls(); gpu=profile.get("gpu",{})
        if gpu.get("pci_id"):
            book.add(CompatibilityFact("gpu",gpu["pci_id"],EvidenceLevel.MACOS_PROVEN if gpu.get("acceleration_status")=="proven" else EvidenceLevel.OBSERVED,"hardware profile"))
        vmd=profile.get("storage",{}).get("vmd",{})
        if vmd.get("ids"):
            book.add(CompatibilityFact("storage.vmd",",".join(vmd["ids"]),EvidenceLevel.MACOS_PROVEN if vmd.get("status")=="proven" else EvidenceLevel.OBSERVED,"hardware profile"))
        return book
