from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..contracts import EvidenceEnvelope
from ..identity import hardware_identity_sha, product_identity_sha
from ..models import HardwareSnapshot
from ..normalize import normalize_snapshot


class DiscoveryProvider(Protocol):
    platform: str
    name: str
    version: str

    def discover(self) -> HardwareSnapshot:
        ...


@dataclass(frozen=True)
class DiscoveryResult:
    snapshot: HardwareSnapshot
    product_identity_sha: str
    hardware_identity_sha: str
    evidence: EvidenceEnvelope

    def to_dict(self) -> dict[str, object]:
        return {
            "snapshot": self.snapshot.to_dict(),
            "product_identity_sha": self.product_identity_sha,
            "hardware_identity_sha": self.hardware_identity_sha,
            "evidence": self.evidence.to_dict(),
        }


def discover_product(
    provider: DiscoveryProvider,
    *,
    source_sha: str = "",
    source_pinned: bool = False,
) -> DiscoveryResult:
    snapshot = normalize_snapshot(provider.discover())
    if snapshot.platform != provider.platform:
        raise ValueError(
            f"discovery provider/platform mismatch: {provider.platform} != {snapshot.platform}"
        )
    snapshot = HardwareSnapshot(
        platform=snapshot.platform,
        product=snapshot.product,
        components=snapshot.components,
        schema_version=snapshot.schema_version,
        discovered_at=snapshot.discovered_at,
        collector=f"{provider.name}@{provider.version}",
        source_pinned=source_pinned,
        source_sha=source_sha,
        metadata={**snapshot.metadata, "provider": provider.name},
    )
    product_sha = product_identity_sha(snapshot.product)
    hardware_sha = hardware_identity_sha(snapshot)
    evidence = EvidenceEnvelope.create(
        source_sha or "UNPINNED_SOURCE",
        "hardware-discovery",
        "OBSERVED",
        {
            "snapshot": snapshot.to_dict(),
            "product_identity_sha": product_sha,
            "hardware_identity_sha": hardware_sha,
        },
        {
            "provider": provider.name,
            "provider_version": provider.version,
            "source_pinned": source_pinned,
        },
    )
    return DiscoveryResult(snapshot, product_sha, hardware_sha, evidence)