from __future__ import annotations

from .base import RuntimeAdapter, RuntimeOperation
from ..platforms import PlatformId


class MacOSRuntime(RuntimeAdapter):
    platform = PlatformId.MACOS

    def operations(self) -> dict[str, RuntimeOperation]:
        return {
            "os.version": RuntimeOperation(
                "os.version",
                ("sw_vers",),
            ),
            "system.identity": RuntimeOperation(
                "system.identity",
                ("system_profiler", "SPHardwareDataType", "-json"),
                timeout_seconds=90,
            ),
            "hardware.pci": RuntimeOperation(
                "hardware.pci",
                ("system_profiler", "SPPCIDataType", "-json"),
                timeout_seconds=90,
            ),
            "hardware.storage": RuntimeOperation(
                "hardware.storage",
                ("system_profiler", "SPStorageDataType", "-json"),
                timeout_seconds=90,
            ),
        }