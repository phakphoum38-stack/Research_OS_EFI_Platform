from __future__ import annotations
import argparse,json
from pathlib import Path
from .acpi_graph import topology_for
from .candidate import generate_candidate
from .collector import write_snapshot
from .multihardware import discover_profiles
from .runtime import write_runtime_event
from .validator import validate_candidate

def main():
    p=argparse.ArgumentParser(prog="hackintosh-platform"); s=p.add_subparsers(dest="command",required=True)
    x=s.add_parser("collect"); x.add_argument("output")
    x=s.add_parser("acpi"); x.add_argument("dsl"); x.add_argument("--name",action="append",default=[])
    x=s.add_parser("candidate"); x.add_argument("profile"); x.add_argument("output")
    x=s.add_parser("validate"); x.add_argument("efi")
    x=s.add_parser("runtime"); x.add_argument("event"); x.add_argument("output"); x.add_argument("--artifact",action="append",default=[])
    x=s.add_parser("profiles"); x.add_argument("--directory",default="hardware")
    a=p.parse_args()
    if a.command=="collect": write_snapshot(a.output)
    elif a.command=="acpi":
        lines=Path(a.dsl).read_text(encoding="utf-8",errors="replace").splitlines()
        print(json.dumps(topology_for(lines,set(a.name or ["GFX0","VMD0","NVD1","ETPD"])),indent=2))
    elif a.command=="candidate":
        print(json.dumps(generate_candidate(json.loads(Path(a.profile).read_text(encoding="utf-8")),a.output),indent=2))
    elif a.command=="validate": print(json.dumps(validate_candidate(a.efi),indent=2))
    elif a.command=="runtime": write_runtime_event(a.event,a.output,a.artifact)
    elif a.command=="profiles": print(json.dumps(discover_profiles(a.directory),indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
