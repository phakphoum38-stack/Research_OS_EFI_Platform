from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from ..models import HardwareComponent, HardwareSnapshot, ProductIdentity
from ..normalize import clean_text


_PCI_RE = re.compile(r"\[([0-9a-fA-F]{4}):([0-9a-fA-F]{4})\]")


def _read(path: str) -> str:
    try:
        return clean_text(Path(path).read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return ""


def _command(argv: list[str]) -> str:
    try:
        result = subprocess.run(
            argv, capture_output=True, text=True, timeout=30, check=False
        )
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


class LinuxDiscovery:
    platform = "linux"
    name = "linux-sysfs-discovery"
    version = "1.0"

    def discover(self) -> HardwareSnapshot:
        identity = ProductIdentity(
            manufacturer=_read("/sys/class/dmi/id/sys_vendor"),
            product=_read("/sys/class/dmi/id/product_name"),
            board=_read("/sys/class/dmi/id/board_name"),
            board_version=_read("/sys/class/dmi/id/board_version"),
            sku=_read("/sys/class/dmi/id/product_sku"),
            bios_vendor=_read("/sys/class/dmi/id/bios_vendor"),
            bios_version=_read("/sys/class/dmi/id/bios_version"),
            bios_date=_read("/sys/class/dmi/id/bios_date"),
        )

        cpu_model = ""
        for line in _read("/proc/cpuinfo").splitlines():
            if line.lower().startswith("model name"):
                cpu_model = clean_text(line.split(":", 1)[-1])
                break
        identity = ProductIdentity(**{**identity.to_dict(), "cpu_model": cpu_model})

        components: list[HardwareComponent] = []
        if cpu_model:
            components.append(
                HardwareComponent(kind="cpu", name=cpu_model, model=cpu_model)
            )

        pci = _command(["lspci", "-Dnn"])
        for line in pci.splitlines():
            matches = _PCI_RE.findall(line)
            if not matches:
                continue
            vendor_id, device_id = matches[-1]
            lower = line.lower()
            if "vga" in lower or "3d controller" in lower or "display controller" in lower:
                kind = "gpu"
            elif "audio" in lower:
                kind = "audio"
            elif "network" in lower or "ethernet" in lower:
                kind = "network"
            elif "non-volatile memory" in lower or "nvme" in lower:
                kind = "storage"
            else:
                kind = "pci"
            components.append(
                HardwareComponent(
                    kind=kind,
                    name=clean_text(line),
                    device_id=f"{vendor_id}:{device_id}".upper(),
                    bus="pci",
                )
            )

        usb = _command(["lsusb"])
        for line in usb.splitlines():
            match = re.search(r"ID\s+([0-9A-Fa-f]{4}):([0-9A-Fa-f]{4})\s+(.*)$", line)
            if match:
                components.append(
                    HardwareComponent(
                        kind="usb",
                        name=clean_text(match.group(3)),
                        device_id=f"{match.group(1)}:{match.group(2)}".upper(),
                        bus="usb",
                    )
                )

        return HardwareSnapshot(
            platform=self.platform,
            product=identity,
            components=tuple(components),
            discovered_at=datetime.now(timezone.utc).isoformat(),
            metadata={"read_only": True, "sources": ["sysfs", "procfs", "lspci", "lsusb"]},
        )