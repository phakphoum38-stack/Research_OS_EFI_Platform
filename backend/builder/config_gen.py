from __future__ import annotations

from typing import Any, Mapping


def generate_config(profile: Mapping[str, Any], kexts: list[str]) -> dict[str, Any]:
    """Create a plist-compatible OpenCore-shaped configuration.

    This is a schema-safe starting point, not a claim that the resulting EFI
    is bootable. Machine-specific ACPI, PlatformInfo and DeviceProperties are
    deliberately added only after evidence is available.
    """
    return {
        "ACPI": {
            "Add": [],
            "Delete": [],
            "Patch": [],
        },
        "Booter": {
            "MmioWhitelist": [],
            "Patch": [],
        },
        "DeviceProperties": {
            "Add": {},
            "Delete": {},
        },
        "Kernel": {
            "Add": [
                {
                    "BundlePath": kext,
                    "Enabled": True,
                    "ExecutablePath": "",
                    "PlistPath": "Contents/Info.plist",
                }
                for kext in kexts
            ],
            "Block": [],
            "Patch": [],
            "Quirks": {},
        },
        "Misc": {
            "Boot": {},
            "Debug": {},
            "Security": {},
            "Tools": [],
        },
        "NVRAM": {
            "Add": {},
            "Delete": {},
            "LegacyOverwrite": False,
            "WriteFlash": True,
        },
        "PlatformInfo": {
            "Generic": {},
        },
        "UEFI": {
            "APFS": {},
            "Drivers": [],
            "Input": {},
            "Output": {},
            "ProtocolOverrides": {},
            "Quirks": {},
            "ReservedMemory": [],
        },
    }
