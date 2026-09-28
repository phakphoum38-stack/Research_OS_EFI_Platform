from dataclasses import dataclass
from .authority import AuthorityBoundary
from .contracts import EvidenceEnvelope
from .efi_knowledge import knowledge_report
from .research_bridge import capability_report
@dataclass(frozen=True)
class ResearchPlan:
 case:dict; stages:tuple; gates:tuple; capabilities:dict; efi_knowledge:dict; authority:dict
 def to_dict(self): return {"schema_version":"1.0","case":self.case,"stages":list(self.stages),"gates":list(self.gates),"capabilities":self.capabilities,"efi_knowledge":self.efi_knowledge,"authority":self.authority}
def build_plan(case):
 return ResearchPlan(case.to_dict(),("COLLECT","NORMALIZE","REASON","BUILD_CANDIDATE","VALIDATE","PREFLIGHT","HUMAN_EXPERIMENT","OBSERVE","EVIDENCE","LEARN"),("PROVENANCE_REQUIRED","FAIL_CLOSED","NO_FIRMWARE_MUTATION","HUMAN_BOOT_BOUNDARY"),capability_report(),knowledge_report(),AuthorityBoundary().evaluate({"owner_authority_required":True,"pre_authority":"HOLD"}))
def plan_envelope(plan): return EvidenceEnvelope.create(plan.case["source_sha"],"research-plan","PLANNED",plan.to_dict(),{"bridge":"research-os","contract":"research-plan/v1"})
