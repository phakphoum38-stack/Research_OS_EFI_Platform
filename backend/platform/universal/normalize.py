from __future__ import annotations

import re

from .models import HardwareComponent, HardwareSnapshot, ProductIdentity


_PCI_RE = re.compile(r"VEN_([0-9A-Fa-f]{4})&DEV_([0-9A-Fa-f]{4})")
_USB_RE = re.compile(r"VID_([0-9A-Fa-f]{4})&PID_([0-9A-Fa-f]{4})")


def clean_text(value: object) -> str:
    return " ".join(str(value or "").replace("\x00", " ").split()).strip()


def normalize_pci_id(value: object) -> str:
    text = clean_text(value).upper()
    match = _PCI_RE.search(text)
    if match:
        return f"{match.group(1)}:{match.group(2)}"
    return text


def normalize_usb_id(value: object) -> str:
    text = clean_text(value).upper()
    match = _USB_RE.search(text)
    if match:
        return f"{match.group(1)}:{match.group(2)}"
    return text


def normalize_identity(identity: ProductIdentity) -> ProductIdentity:
    return ProductIdentity(
        manufacturer=clean_text(identity.manufacturer),
        product=clean_text(identity.product),
        board=clean_text(identity.board),
        board_version=clean_text(identity.board_version),
        sku=clean_text(identity.sku),
        bios_vendor=clean_text(identity.bios_vendor),
        bios_version=clean_text(identity.bios_version),
        bios_date=clean_text(identity.bios_date),
        cpu_model=clean_text(identity.cpu_model),
    )


def normalize_component(component: HardwareComponent) -> HardwareComponent:
    device_id = component.device_id
    if component.bus.lower() == "pci":
        device_id = normalize_pci_id(device_id)
    elif component.bus.lower() == "usb":
        device_id = normalize_usb_id(device_id)
    return HardwareComponent(
        kind=clean_text(component.kind).lower(),
        name=clean_text(component.name),
        vendor=clean_text(component.vendor),
        model=clean_text(component.model),
        device_id=clean_text(device_id),
        bus=clean_text(component.bus).lower(),
        driver=clean_text(component.driver),
        properties={clean_text(k): v for k, v in component.properties.items()},
    )


def normalize_snapshot(snapshot: HardwareSnapshot) -> HardwareSnapshot:
    components = tuple(
        sorted(
            (normalize_component(item) for item in snapshot.components),
            key=lambda item: (
                item.kind,
                item.bus,
                item.device_id,
                item.vendor,
                item.model,
                item.name,
            ),
        )
    )
    return HardwareSnapshot(
        platform=clean_text(snapshot.platform).lower(),
        product=normalize_identity(snapshot.product),
        components=components,
        schema_version=snapshot.schema_version,
        discovered_at=clean_text(snapshot.discovered_at),
        collector=clean_text(snapshot.collector),
        source_pinned=snapshot.source_pinned,
        source_sha=clean_text(snapshot.source_sha),
        metadata=dict(snapshot.metadata),
    )