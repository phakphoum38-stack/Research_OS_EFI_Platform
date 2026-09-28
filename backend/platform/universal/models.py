from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProductIdentity:
    manufacturer: str = ""
    product: str = ""
    board: str = ""
    board_version: str = ""
    sku: str = ""
    bios_vendor: str = ""
    bios_version: str = ""
    bios_date: str = ""
    cpu_model: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            key: str(value)
            for key, value in asdict(self).items()
            if str(value).strip()
        }


@dataclass(frozen=True)
class HardwareComponent:
    kind: str
    name: str = ""
    vendor: str = ""
    model: str = ""
    device_id: str = ""
    bus: str = ""
    driver: str = ""
    properties: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "name": self.name,
            "vendor": self.vendor,
            "model": self.model,
            "device_id": self.device_id,
            "bus": self.bus,
            "driver": self.driver,
            "properties": dict(self.properties),
        }


@dataclass(frozen=True)
class HardwareSnapshot:
    platform: str
    product: ProductIdentity
    components: tuple[HardwareComponent, ...] = ()
    schema_version: str = "1.0"
    discovered_at: str = ""
    collector: str = ""
    source_pinned: bool = False
    source_sha: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "platform": self.platform,
            "discovered_at": self.discovered_at,
            "collector": self.collector,
            "source_pinned": self.source_pinned,
            "source_sha": self.source_sha,
            "product": self.product.to_dict(),
            "components": [item.to_dict() for item in self.components],
            "metadata": dict(self.metadata),
        }