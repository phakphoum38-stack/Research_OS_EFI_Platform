from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

from ...contracts import EvidenceEnvelope, verify_envelope
from ..identity import (
    discovery_snapshot_sha,
    hardware_identity_sha,
    product_identity_sha,
)
from ..models import HardwareSnapshot
from ..normalize import normalize_snapshot


_SHA256_RE = re.compile(r"^[0-9a-fA-F]{40}$")


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
    discovery_snapshot_sha: str
    evidence: EvidenceEnvelope

    def to_dict(self) -> dict[str, object]:
        return {
            "snapshot": self.snapshot.to_dict(),
            "product_identity_sha": self.product_identity_sha,
            "hardware_identity_sha": self.hardware_identity_sha,
            "discovery_snapshot_sha": self.discovery_snapshot_sha,
            "evidence": self.evidence.to_dict(),
        }


def discover_product(
    provider: DiscoveryProvider,
    *,
    source_sha: str = "",
    source_pinned: bool = False,
) -> DiscoveryResult:
    if source_pinned and not _SHA256_RE.fullmatch(source_sha):
        raise ValueError("source_pinned discovery requires a 40-character SHA-1 commit identifier")
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
    snapshot_sha = discovery_snapshot_sha(snapshot)
    physical_machine = bool(snapshot.metadata.get("physical_machine", False))
    effective_source = source_sha or "UNPINNED_SOURCE"
    evidence = EvidenceEnvelope.create(
        effective_source,
        "hardware-discovery",
        "OBSERVED",
        {
            "snapshot": snapshot.to_dict(),
            "product_identity_sha": product_sha,
            "hardware_identity_sha": hardware_sha,
            "discovery_snapshot_sha": snapshot_sha,
        },
        {
            "evidence_schema": "discovery-v3",
            "platform": snapshot.platform,
            "collector": snapshot.collector,
            "provider": provider.name,
            "provider_version": provider.version,
            "source_pinned": source_pinned,
            "read_only": bool(snapshot.metadata.get("read_only")),
            "physical_machine": physical_machine,
        },
    )
    if not verify_envelope(evidence.to_dict()):
        raise RuntimeError("hardware discovery produced unverifiable evidence envelope")
    return DiscoveryResult(snapshot, product_sha, hardware_sha, snapshot_sha, evidence)
