from dataclasses import dataclass,asdict
@dataclass(frozen=True)
class EFIKnowledge:
 component:str; requirement:str; state:str; evidence_required:str; note:str
X1504VA_EFI_KNOWLEDGE=(
 EFIKnowledge("GPU 8086:A7A9","macOS acceleration","RESEARCH","macOS runtime evidence","ACPI GFX0 is not QE/CI proof."),
 EFIKnowledge("VMD 8086:09AB/A77F","macOS storage","RESEARCH","macOS runtime evidence","Windows iaStorVD is not macOS proof."),
 EFIKnowledge("ALC256 10EC:0256","AppleALC family","PROVEN","codec/layout evidence","Layout remains separate."),
 EFIKnowledge("MT7902 14C3:7902","macOS Wi-Fi","RESEARCH","macOS runtime evidence","Windows driver is not macOS proof."),
 EFIKnowledge("ASUF1300","macOS touchpad","RESEARCH","macOS runtime evidence","ACPI wiring is not runtime support."))
def knowledge_report(): return {"schema_version":"1.0","domain":"efi-opencore","facts":[asdict(x) for x in X1504VA_EFI_KNOWLEDGE]}
