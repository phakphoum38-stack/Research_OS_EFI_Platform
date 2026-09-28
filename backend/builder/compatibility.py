from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class CompatibilityResult:
    status: str
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    proven: tuple[str, ...]


def evaluate_hardware(profile: Mapping[str, Any]) -> CompatibilityResult:
    """Evaluate evidence before generating an EFI candidate.

    This is intentionally conservative: unknown macOS support is not converted
    into a working-kext claim.
    """
    blockers: list[str] = []
    warnings: list[str] = []
    proven: list[str] = []

    gpu = profile.get("gpu", {})
    if gpu.get("pci_id") == "8086:A7A9":
        if gpu.get("acceleration_status") != "proven":
            blockers.append("Intel UHD 8086:A7A9 acceleration is not proven")
        else:
            proven.append("Intel UHD 8086:A7A9 acceleration")
    else:
        warnings.append("GPU identity is not the known X1504VA profile")

    storage = profile.get("storage", {})
    vmd = storage.get("vmd", {})
    if vmd.get("status") != "proven":
        blockers.append("Intel VMD storage path is not proven")
    else:
        proven.append("Intel VMD storage path")

    audio = profile.get("audio", {})
    if audio.get("codec") == "10EC:0256" and audio.get("applealc_status") == "proven":
        proven.append("Realtek ALC256 codec family")
    else:
        warnings.append("Audio codec support is not proven")

    wifi = profile.get("wifi", {})
    if wifi.get("macos_status") != "proven":
        warnings.append("MediaTek MT7902 macOS support is not proven")

    touchpad = profile.get("touchpad", {})
    if touchpad.get("acpi_status") != "proven":
        warnings.append("X1504VA touchpad ACPI path is not proven")

    status = "READY" if not blockers else "BLOCKED"
    return CompatibilityResult(
        status=status,
        blockers=tuple(blockers),
        warnings=tuple(warnings),
        proven=tuple(proven),
    )


def result_to_dict(result: CompatibilityResult) -> dict[str, Any]:
    return {
        "status": result.status,
        "blockers": list(result.blockers),
        "warnings": list(result.warnings),
        "proven": list(result.proven),
    }
