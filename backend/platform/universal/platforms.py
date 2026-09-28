from __future__ import annotations

import sys
from dataclasses import asdict, dataclass
from enum import Enum


class PlatformId(str, Enum):
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    FREEBSD = "freebsd"
    OPENBSD = "openbsd"
    NETBSD = "netbsd"
    OTHER = "other"


@dataclass(frozen=True)
class PlatformDescriptor:
    platform_id: PlatformId
    display_name: str
    runtime_module: str
    discovery_module: str
    owns_compatibility_domain: bool = True


PLATFORM_REGISTRY: dict[PlatformId, PlatformDescriptor] = {
    PlatformId.WINDOWS: PlatformDescriptor(
        PlatformId.WINDOWS,
        "Windows",
        "backend.platform.universal.runtime.windows",
        "backend.platform.universal.discovery.windows",
    ),
    PlatformId.LINUX: PlatformDescriptor(
        PlatformId.LINUX,
        "Linux",
        "backend.platform.universal.runtime.linux",
        "backend.platform.universal.discovery.linux",
    ),
    PlatformId.MACOS: PlatformDescriptor(
        PlatformId.MACOS,
        "macOS",
        "backend.platform.universal.runtime.macos",
        "backend.platform.universal.discovery.macos",
    ),
    PlatformId.FREEBSD: PlatformDescriptor(
        PlatformId.FREEBSD,
        "FreeBSD",
        "external.runtime.freebsd",
        "external.discovery.freebsd",
    ),
    PlatformId.OPENBSD: PlatformDescriptor(
        PlatformId.OPENBSD,
        "OpenBSD",
        "external.runtime.openbsd",
        "external.discovery.openbsd",
    ),
    PlatformId.NETBSD: PlatformDescriptor(
        PlatformId.NETBSD,
        "NetBSD",
        "external.runtime.netbsd",
        "external.discovery.netbsd",
    ),
    PlatformId.OTHER: PlatformDescriptor(
        PlatformId.OTHER,
        "Other",
        "external.runtime.other",
        "external.discovery.other",
    ),
}


def host_platform() -> PlatformId:
    if sys.platform == "win32":
        return PlatformId.WINDOWS
    if sys.platform == "darwin":
        return PlatformId.MACOS
    if sys.platform.startswith("linux"):
        return PlatformId.LINUX
    return PlatformId.OTHER


def normalize_platform(value: str | PlatformId) -> PlatformId:
    if isinstance(value, PlatformId):
        return value
    text = str(value).strip().lower()
    aliases = {
        "win": PlatformId.WINDOWS,
        "windows": PlatformId.WINDOWS,
        "linux": PlatformId.LINUX,
        "mac": PlatformId.MACOS,
        "macos": PlatformId.MACOS,
        "osx": PlatformId.MACOS,
        "freebsd": PlatformId.FREEBSD,
        "openbsd": PlatformId.OPENBSD,
        "netbsd": PlatformId.NETBSD,
        "other": PlatformId.OTHER,
    }
    try:
        return aliases[text]
    except KeyError as exc:
        raise ValueError(f"unsupported platform: {value}") from exc


def platform_report() -> dict[str, object]:
    current = host_platform()
    return {
        "schema_version": "1.0",
        "host_platform": current.value,
        "platforms": [
            {
                **asdict(descriptor),
                "platform_id": descriptor.platform_id.value,
            }
            for descriptor in PLATFORM_REGISTRY.values()
        ],
    }