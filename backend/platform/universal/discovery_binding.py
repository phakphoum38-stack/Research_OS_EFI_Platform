from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.platform.universal.catalog import ProductCatalog, ProductMatch
from backend.platform.universal.identity import discovery_snapshot_sha, hardware_identity_sha
from backend.platform.universal.models import HardwareSnapshot


@dataclass(frozen=True)
class DiscoveryProductBinding:
    """Auditable binding between one machine observation and catalog matches.

    Binding is descriptive only: it does not promote compatibility or alter EFI state.
    """

    discovery_snapshot_sha: str
    hardware_identity_sha: str
    product_identity: dict[str, Any]
    matches: tuple[ProductMatch, ...]

    @property
    def status(self) -> str:
        if not self.matches:
            return "UNMATCHED"
        if len(self.matches) > 1:
            return "AMBIGUOUS"
        return "MATCHED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "discovery_snapshot_sha": self.discovery_snapshot_sha,
            "hardware_identity_sha": self.hardware_identity_sha,
            "product_identity": dict(self.product_identity),
            "status": self.status,
            "matches": [match.to_dict() for match in self.matches],
        }


def bind_discovery_to_product_catalog(
    snapshot: HardwareSnapshot,
    catalog: ProductCatalog,
) -> DiscoveryProductBinding:
    """Bind a normalized discovery snapshot to catalog records by observed identity.

    The binding carries deterministic observation identities and catalog match evidence.
    It never infers compatibility, truth, or platform support.
    """
    matches = tuple(catalog.match(snapshot))
    return DiscoveryProductBinding(
        discovery_snapshot_sha=discovery_snapshot_sha(snapshot),
        hardware_identity_sha=hardware_identity_sha(snapshot),
        product_identity=snapshot.product.to_dict(),
        matches=matches,
    )
