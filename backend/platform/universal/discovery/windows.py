from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from typing import Any

from ..models import HardwareComponent, HardwareSnapshot, ProductIdentity
from ..normalize import clean_text, normalize_pci_id, normalize_usb_id


_PCI_RE = re.compile(r"VEN_([0-9A-Fa-f]{4})&DEV_([0-9A-Fa-f]{4})")
_USB_RE = re.compile(r"VID_([0-9A-Fa-f]{4})&PID_([0-9A-Fa-f]{4})")


class WindowsDiscovery:
    platform = "windows"
    name = "windows-cim-discovery"
    version = "1.0"

    _queries = {
        "computer": "Get-CimInstance Win32_ComputerSystem | Select Manufacturer,Model,SystemFamily,SystemSKUNumber",
        "baseboard": "Get-CimInstance Win32_BaseBoard | Select Manufacturer,Product,Version",
        "bios": "Get-CimInstance Win32_BIOS | Select Manufacturer,SMBIOSBIOSVersion,ReleaseDate",
        "cpu": "Get-CimInstance Win32_Processor | Select Name,Manufacturer,ProcessorId,NumberOfCores,NumberOfLogicalProcessors",
        "gpu": "Get-CimInstance Win32_VideoController | Select Name,PNPDeviceID,DriverVersion,AdapterCompatibility",
        "storage": "Get-CimInstance Win32_DiskDrive | Select Model,InterfaceType,Size,PNPDeviceID",
        "network": "Get-CimInstance Win32_NetworkAdapter -Filter 'PhysicalAdapter = TRUE' | Select Name,PNPDeviceID,Manufacturer,DriverVersion,NetConnectionStatus",
        "audio": "Get-CimInstance Win32_SoundDevice | Select Name,PNPDeviceID,Manufacturer,Status",
        "pnp": "Get-CimInstance Win32_PnPEntity | Where-Object { $_.PNPDeviceID -and ($_.PNPDeviceID -match '^(PCI\\|USB\\)') } | Select Name,Manufacturer,PNPDeviceID,PNPClass,DriverVersion",
    }

    def _query(self, name: str, expression: str) -> list[dict[str, Any]]:
        command = (
            "& { "
            + expression
            + " | ConvertTo-Json -Compress -Depth 6 "
            + " }"
        )
        try:
            result = subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    command,
                ],
                capture_output=True,
                text=True,
                timeout=45,
                check=False,
            )
        except (FileNotFoundError, OSError, subprocess.SubprocessError) as exc:
            raise RuntimeError("Windows discovery requires powershell.exe") from exc
        if result.returncode != 0:
            raise RuntimeError(f"Windows discovery query failed: {name}: {result.stderr.strip()}")
        if not result.stdout.strip():
            return []
        try:
            value = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"invalid JSON from Windows discovery query: {name}") from exc
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            return [value]
        return []

    @staticmethod
    def _first(rows: list[dict[str, Any]]) -> dict[str, Any]:
        return rows[0] if rows else {}

    @staticmethod
    def _pci_from_pnp(value: object) -> str:
        match = _PCI_RE.search(clean_text(value))
        return f"{match.group(1)}:{match.group(2)}".upper() if match else normalize_pci_id(value)

    @staticmethod
    def _usb_from_pnp(value: object) -> str:
        match = _USB_RE.search(clean_text(value))
        return f"{match.group(1)}:{match.group(2)}".upper() if match else normalize_usb_id(value)

    def discover(self) -> HardwareSnapshot:
        data = {
            name: self._query(name, expression)
            for name, expression in self._queries.items()
        }
        computer = self._first(data["computer"])
        board = self._first(data["baseboard"])
        bios = self._first(data["bios"])
        cpu = self._first(data["cpu"])

        product = ProductIdentity(
            manufacturer=clean_text(computer.get("Manufacturer")),
            product=clean_text(computer.get("Model")),
            board=clean_text(board.get("Product") or computer.get("Model")),
            board_version=clean_text(board.get("Version")),
            sku=clean_text(computer.get("SystemSKUNumber")),
            bios_vendor=clean_text(bios.get("Manufacturer")),
            bios_version=clean_text(bios.get("SMBIOSBIOSVersion")),
            bios_date=clean_text(bios.get("ReleaseDate")),
            cpu_model=clean_text(cpu.get("Name")),
        )

        components: list[HardwareComponent] = []
        if cpu:
            components.append(
                HardwareComponent(
                    kind="cpu",
                    name=clean_text(cpu.get("Name")),
                    vendor=clean_text(cpu.get("Manufacturer")),
                    model=clean_text(cpu.get("Name")),
                    device_id=clean_text(cpu.get("ProcessorId")),
                    properties={
                        "cores": cpu.get("NumberOfCores"),
                        "logical_processors": cpu.get("NumberOfLogicalProcessors"),
                    },
                )
            )

        for row in data["gpu"]:
            components.append(
                HardwareComponent(
                    kind="gpu",
                    name=clean_text(row.get("Name")),
                    vendor=clean_text(row.get("AdapterCompatibility")),
                    model=clean_text(row.get("Name")),
                    device_id=self._pci_from_pnp(row.get("PNPDeviceID")),
                    bus="pci",
                    driver=clean_text(row.get("DriverVersion")),
                )
            )

        for row in data["storage"]:
            components.append(
                HardwareComponent(
                    kind="storage",
                    name=clean_text(row.get("Model")),
                    model=clean_text(row.get("Model")),
                    device_id=self._pci_from_pnp(row.get("PNPDeviceID")),
                    properties={
                        "interface": clean_text(row.get("InterfaceType")),
                        "size": row.get("Size"),
                    },
                )
            )

        for row in data["network"]:
            components.append(
                HardwareComponent(
                    kind="network",
                    name=clean_text(row.get("Name")),
                    vendor=clean_text(row.get("Manufacturer")),
                    device_id=self._pci_from_pnp(row.get("PNPDeviceID")),
                    bus="pci",
                    driver=clean_text(row.get("DriverVersion")),
                    properties={"status": row.get("NetConnectionStatus")},
                )
            )

        for row in data["audio"]:
            components.append(
                HardwareComponent(
                    kind="audio",
                    name=clean_text(row.get("Name")),
                    vendor=clean_text(row.get("Manufacturer")),
                    device_id=self._pci_from_pnp(row.get("PNPDeviceID")),
                    bus="pci",
                    properties={"status": clean_text(row.get("Status"))},
                )
            )

        for row in data["pnp"]:
            pnp = clean_text(row.get("PNPDeviceID"))
            if pnp.upper().startswith("USB\\"):
                device_id = self._usb_from_pnp(pnp)
                bus = "usb"
            else:
                device_id = self._pci_from_pnp(pnp)
                bus = "pci"
            components.append(
                HardwareComponent(
                    kind=clean_text(row.get("PNPClass")) or "device",
                    name=clean_text(row.get("Name")),
                    vendor=clean_text(row.get("Manufacturer")),
                    device_id=device_id,
                    bus=bus,
                    driver=clean_text(row.get("DriverVersion")),
                )
            )

        return HardwareSnapshot(
            platform=self.platform,
            product=product,
            components=tuple(components),
            discovered_at=datetime.now(timezone.utc).isoformat(),
            metadata={
                "read_only": True,
                "queries": list(self._queries.keys()),
                "query_count": len(self._queries),
            },
        )