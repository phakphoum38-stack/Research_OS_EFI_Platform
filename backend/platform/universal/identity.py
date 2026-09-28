from __future__ import annotations

import hashlib
import json
from typing import Any

from .models import HardwareSnapshot, ProductIdentity


def _digest(value: dict[str, Any]) -> str:
    encoded = (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def product_identity_payload(identity: ProductIdentity) -> dict[str, str]:
    return {
        "manufacturer": identity.manufacturer,
        "product": identity.product,
        "board": identity.board,
        "board_version": identity.board_version,
        "sku": identity.sku,
        "bios_vendor": identity.bios_vendor,
        "bios_version": identity.bios_version,
    }


def hardware_identity_payload(snapshot: HardwareSnapshot) -> dict[str, Any]:
    stable_components = []
    for component in snapshot.components:
        stable_components.append(
            {
                "kind": component.kind,
                "bus": component.bus,
                "device_id": component.device_id,
                "vendor": component.vendor,
                "model": component.model,
            }
        )
    stable_components.sort(
        key=lambda item: (
            item["kind"],
            item["bus"],
            item["device_id"],
            item["vendor"],
            item["model"],
        )
    )
    return {
        "product": product_identity_payload(snapshot.product),
        "cpu_model": snapshot.product.cpu_model,
        "components": stable_components,
    }


def product_identity_sha(identity: ProductIdentity) -> str:
    return _digest(product_identity_payload(identity))


def hardware_identity_sha(snapshot: HardwareSnapshot) -> str:
    return _digest(hardware_identity_payload(snapshot))