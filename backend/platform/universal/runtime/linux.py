from __future__ import annotations

from .base import RuntimeAdapter, RuntimeOperation
from ..platforms import PlatformId


class LinuxRuntime(RuntimeAdapter):
    platform = PlatformId.LINUX

    def operations(self) -> dict[str, RuntimeOperation]:
        return {
            "os.version": RuntimeOperation(
                "os.version",
                ("uname", "-srvm"),
            ),
            "system.identity": RuntimeOperation(
                "system.identity",
                ("cat", "/sys/class/dmi/id/product_name"),
            ),
            "hardware.pci": RuntimeOperation(
                "hardware.pci",
                ("lspci", "-Dnn"),
            ),
            "hardware.usb": RuntimeOperation(
                "hardware.usb",
                ("lsusb",),
            ),
        }