from __future__ import annotations
import json, platform, subprocess
from datetime import datetime, timezone
from typing import Any

def _powershell(command: str) -> str:
    try:
        p = subprocess.run(["powershell.exe","-NoProfile","-Command",command],capture_output=True,text=True,timeout=30)
        return p.stdout.strip()
    except (FileNotFoundError, subprocess.SubprocessError):
        return ""

def collect_windows() -> dict[str, Any]:
    return {"schema_version":"1.0","collected_at":datetime.now(timezone.utc).isoformat(),"platform":platform.platform(),
            "computer":json.loads(x) if (x:=_powershell("Get-CimInstance Win32_ComputerSystem | ConvertTo-Json -Compress")) else None,
            "bios":json.loads(x) if (x:=_powershell("Get-CimInstance Win32_BIOS | ConvertTo-Json -Compress")) else None,
            "disks":json.loads(x) if (x:=_powershell("Get-CimInstance Win32_DiskDrive | Select Model,InterfaceType,Size | ConvertTo-Json -Compress")) else None}

def write_snapshot(path: str) -> None:
    with open(path,"w",encoding="utf-8") as f: json.dump(collect_windows(),f,indent=2,ensure_ascii=False); f.write("\n")
