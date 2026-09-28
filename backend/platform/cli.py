from __future__ import annotations
import argparse,json
from pathlib import Path
from .acpi_graph import topology_for
from .candidate import generate_candidate
from .collector import write_snapshot
from .multihardware import discover_profiles
from .preflight import build_preflight,write_preflight
from .runtime import write_runtime_event
from .validator import validate_candidate
from .research_bridge import capability_report
from .efi_knowledge import knowledge_report
from .research_case import ResearchCase
from .orchestrator import build_plan
from .opencore import validate_opencore\nfrom .pipeline import build_evidence_packet,write_evidence_packet
def main():
 p=argparse.ArgumentParser(prog="hackintosh-platform"); s=p.add_subparsers(dest="command",required=True)
 x=s.add_parser("collect"); x.add_argument("output")
 x=s.add_parser("acpi"); x.add_argument("dsl"); x.add_argument("--name",action="append",default=[])
 x=s.add_parser("candidate"); x.add_argument("profile"); x.add_argument("output")
 x=s.add_parser("validate"); x.add_argument("efi")
 x=s.add_parser("preflight"); x.add_argument("profile"); x.add_argument("efi"); x.add_argument("experiment"); x.add_argument("output")
 x=s.add_parser("runtime"); x.add_argument("event"); x.add_argument("output"); x.add_argument("--artifact",action="append",default=[])
 x=s.add_parser("profiles"); x.add_argument("--directory",default="hardware")
 s.add_parser("bridge"); s.add_parser("efi-knowledge")
 x=s.add_parser("validate-opencore"); x.add_argument("efi")
 x=s.add_parser("plan"); x.add_argument("profile"); x.add_argument("--source-sha",required=True); x.add_argument("--case-id",default="x1504va-research")\n x=s.add_parser("pipeline"); x.add_argument("profile"); x.add_argument("output"); x.add_argument("--source-sha",required=True); x.add_argument("--hypothesis",required=True); x.add_argument("--case-id",default="x1504va-research")
 a=p.parse_args()
 if a.command=="collect": write_snapshot(a.output)
 elif a.command=="acpi":
  lines=Path(a.dsl).read_text(encoding="utf-8",errors="replace").splitlines(); print(json.dumps(topology_for(lines,set(a.name or ["GFX0","VMD0","NVD1","ETPD"])),indent=2))
 elif a.command=="candidate": print(json.dumps(generate_candidate(json.loads(Path(a.profile).read_text(encoding="utf-8")),a.output),indent=2))
 elif a.command=="validate": print(json.dumps(validate_candidate(a.efi),indent=2))
 elif a.command=="preflight":
  r=build_preflight(json.loads(Path(a.profile).read_text(encoding="utf-8")),a.efi,json.loads(Path(a.experiment).read_text(encoding="utf-8"))); write_preflight(r,a.output); print(json.dumps(r,indent=2))
 elif a.command=="runtime": write_runtime_event(a.event,a.output,a.artifact)
 elif a.command=="profiles": print(json.dumps(discover_profiles(a.directory),indent=2))
 elif a.command=="bridge": print(json.dumps(capability_report(),indent=2))
 elif a.command=="efi-knowledge": print(json.dumps(knowledge_report(),indent=2))
 elif a.command=="validate-opencore": print(json.dumps(validate_opencore(a.efi),indent=2))
 elif a.command=="pipeline":\n  profile=json.loads(Path(a.profile).read_text(encoding="utf-8"))\n  packet=build_evidence_packet(profile,a.output,a.source_sha,a.hypothesis,a.case_id)\n  out=Path(a.output)/"evidence-packet.json"; write_evidence_packet(packet,str(out)); print(json.dumps(packet,indent=2))\n elif a.command=="plan":
  profile=json.loads(Path(a.profile).read_text(encoding="utf-8"))
  case=ResearchCase.from_profile(a.case_id,a.source_sha,"X1504VA","controlled evidence-first EFI research",profile,capability_report()["capabilities"])
  print(json.dumps(build_plan(case).to_dict(),indent=2))
 return 0
if __name__=="__main__": raise SystemExit(main())
