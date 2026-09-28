import unittest
from backend.platform.authority import AuthorityBoundary
from backend.platform.contracts import EvidenceEnvelope,verify_envelope
from backend.platform.efi_knowledge import knowledge_report
from backend.platform.orchestrator import build_plan,plan_envelope
from backend.platform.research_bridge import capability_report
from backend.platform.research_case import ResearchCase
class PlatformFoundationTests(unittest.TestCase):
 def test_bridge_provenance(self):
  r=capability_report(); self.assertEqual(r["source_policy"],"PROVENANCE_REQUIRED"); self.assertTrue(all(x["source_sha"] for x in r["capabilities"]))
 def test_envelope(self):
  self.assertTrue(verify_envelope(EvidenceEnvelope.create("a"*40,"runtime","OBSERVED",{"ok":True},{"source":"test"}).to_dict()))
 def test_authority_never_mutates(self):
  r=AuthorityBoundary().evaluate({"owner_authority_required":True,"pre_authority":"PASS"},True); self.assertTrue(r["merge_authorized"]); self.assertFalse(r["hardware_mutation_authorized"])
 def test_plan_closed(self):
  p=build_plan(ResearchCase.from_profile("case-1","a"*40,"X1504VA","controlled research",{"gpu":{"state":"research"}},[])); self.assertFalse(p.authority["merge_authorized"]); self.assertIn("HUMAN_BOOT_BOUNDARY",p.gates); self.assertTrue(verify_envelope(plan_envelope(p).to_dict()))
 def test_efi_unknowns_preserved(self): self.assertIn("RESEARCH",{x["state"] for x in knowledge_report()["facts"]})
