from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from typing import Any

from ..models import HardwareComponent, HardwareSnapshot, ProductIdentity
from ..normalize import clean_text


def _json_command(argv: list[str]) -> dict[str, Any]:
    try:
        result = subprocess.run(
            argv, capture_output=True, text=True, timeout=90, check=False
        )
    except (FileNotFoundError, OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError(f"macOS discovery command unavailable: {argv[0]}") from exc
    if result.returncode != 0:
        raise RuntimeError(f"macOS discovery command failed: {' '.join(argv)}")
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("invalid JSON from macOS discovery command") from exc
    return value if isinstance(value, dict) else {}


def _find_dicts(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        found.append(value)
        for child in value.values():
            found.extend(_find_dicts(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(_find_dicts(child))
    return found


def _first_value(rows: list[dict[str, Any]], *keys: str) -> str:
    for row in rows:
        for key in keys:
            if key in row and clean_text(row[key]):
                return clean_text(row[key])
    return ""


class MacOSDiscovery:
    platform = "macos"
    name = "macos-system-profiler-discovery"
    version = "1.0"

    def discover(self) -> HardwareSnapshot:
        hardware = _json_command(["system_profiler", "SPHardwareDataType", "-json"])
        rows = _find_dicts(hardware)

        identity = ProductIdentity(
            manufacturer="Apple",
            product=_first_value(rows, "machine_name", "machine_model"),
            board=_first_value(rows, "board_id"),
            board_version=_first_value(rows, "boot_rom_version"),
            bios_vendor="Apple",
            bios_version=_first_value(rows, "boot_rom_version", "system_firmware_version"),
            cpu_model=_first_value(rows, "cpu_type", "chip_type"),
        )

        components: list[HardwareComponent] = []
        for profile_type, kind, bus in (
            ("SPPCIDataType", "pci", "pci"),
            ("SPStorageDataType", "storage", ""),
            ("SPUSBDataType", "usb", "usb"),
            ("SPAudioDataType", "audio", ""),
            ("SPNetworkDataType", "network", ""),
        ):
            try:
                payload = _json_command(["system_profiler", profile_type, "-json"])
            except RuntimeError:
                continue
            for row in _find_dicts(payload):
                name = _first_value(
                    [row],
                    "_name",
                    "sppci_model",
                    "sppci_name",
                    "device_name",
                )
                vendor = _first_value(
                    [row], "sppci_vendor", "manufacturer", "spusb_vendor"
                )
                vendor_id = _first_value([row], "sppci_vendor-id", "vendor-id")
                device_id = _first_value([row], "sppci_device-id", "device-id")
                normalized_id = ""
                if vendor_id and device_id:
                    vendor_id = vendor_id.replace("0x", "").zfill(4)[-4:]
                    device_id = device_id.replace("0x", "").zfill(4)[-4:]
                    normalized_id = f"{vendor_id}:{device_id}".upper()
                if name or vendor or normalized_id:
                    components.append(
                        HardwareComponent(
                            kind=kind,
                            name=name,
                            vendor=vendor,
                            model=name,
                            device_id=normalized_id,
                            bus=bus,
                        )
                    )

        return HardwareSnapshot(
            platform=self.platform,
            product=identity,
            components=tuple(components),
            discovered_at=datetime.now(timezone.utc).isoformat(),
            metadata={"read_only": True, "source": "system_profiler"},
        )