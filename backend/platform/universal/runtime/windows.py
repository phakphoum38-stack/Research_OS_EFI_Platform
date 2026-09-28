from __future__ import annotations

from .base import RuntimeAdapter, RuntimeOperation
from ..platforms import PlatformId


class WindowsRuntime(RuntimeAdapter):
    platform = PlatformId.WINDOWS

    def operations(self) -> dict[str, RuntimeOperation]:
        return {
            "os.version": RuntimeOperation(
                "os.version",
                (
                    "powershell.exe",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    "$PSVersionTable.PSVersion.ToString()",
                ),
            ),
            "system.identity": RuntimeOperation(
                "system.identity",
                (
                    "powershell.exe",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    "Get-CimInstance Win32_ComputerSystemProduct | "
                    "Select Vendor,Name,Version | ConvertTo-Json -Compress",
                ),
            ),
            "hardware.pnp": RuntimeOperation(
                "hardware.pnp",
                (
                    "powershell.exe",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    "Get-CimInstance Win32_PnPEntity | "
                    "Select Name,Manufacturer,PNPDeviceID,PNPClass,DriverVersion | "
                    "ConvertTo-Json -Compress -Depth 4",
                ),
            ),
        }