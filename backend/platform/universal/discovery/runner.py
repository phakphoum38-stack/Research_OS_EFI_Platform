from __future__ import annotations

from ..platforms import PlatformId, normalize_platform
from . import DiscoveryProvider
from .linux import LinuxDiscovery
from .macos import MacOSDiscovery
from .windows import WindowsDiscovery


_PROVIDERS = {
    PlatformId.WINDOWS: WindowsDiscovery,
    PlatformId.LINUX: LinuxDiscovery,
    PlatformId.MACOS: MacOSDiscovery,
}


def provider_for(platform: str | PlatformId) -> DiscoveryProvider:
    target = normalize_platform(platform)
    provider_type = _PROVIDERS.get(target)
    if provider_type is None:
        raise ValueError(f"no local discovery provider registered for {target.value}")
    return provider_type()