from __future__ import annotations

from typing import Any, Mapping


def resolve_kexts(profile: Mapping[str, Any]) -> list[str]:
    """Return only evidence-backed kext candidates."""
    kexts = ["Lilu.kext", "VirtualSMC.kext"]

    gpu = profile.get("gpu", {})
    if gpu.get("acceleration_status") == "proven":
        kexts.append("WhateverGreen.kext")

    audio = profile.get("audio", {})
    if audio.get("applealc_status") == "proven":
        kexts.append("AppleALC.kext")

    wifi = profile.get("wifi", {})
    if wifi.get("macos_status") == "proven":
        kexts.append("WiFi.kext")

    return kexts
