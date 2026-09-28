from __future__ import annotations
import json, plistlib
from pathlib import Path
REQUIRED_DIRS=("ACPI","Kexts","Drivers","Resources","Tools")

def validate_candidate(root: str) -> dict:
    base=Path(root)/"OC"; errors=[]; warnings=[]
    if not base.is_dir(): errors.append("EFI/OC directory is missing")
    for name in REQUIRED_DIRS:
        if not (base/name).is_dir(): errors.append(f"EFI/OC/{name} directory is missing")
    report=base/"compatibility-report.json"
    if report.is_file():
        try:
            data=json.loads(report.read_text(encoding="utf-8"))
            if data.get("status")=="BLOCKED": warnings.append("candidate carries a blocked compatibility report")
        except json.JSONDecodeError: errors.append("compatibility-report.json is invalid JSON")
    plist=base/"config.plist"
    if plist.exists():
        try:
            with plist.open("rb") as f: plistlib.load(f)
        except Exception as exc: errors.append(f"config.plist is invalid: {exc}")
    else: warnings.append("config.plist is absent; candidate is non-bootable by design")
    return {"status":"PASS" if not errors else "FAIL","errors":errors,"warnings":warnings}
