import json,plistlib,tempfile,unittest
from pathlib import Path
from backend.platform.opencore import validate_opencore
class OpenCoreValidationTests(unittest.TestCase):
 def test_blocked_candidate_is_inspectable(self):
  with tempfile.TemporaryDirectory() as d:
   oc=Path(d)/"OC"
   for x in ("ACPI","Kexts","Drivers","Resources","Tools"): (oc/x).mkdir(parents=True)
   (oc/"compatibility-report.json").write_text(json.dumps({"status":"EFI_BLOCKED"}),encoding="utf-8")
   r=validate_opencore(d); self.assertEqual(r["status"],"PASS"); self.assertTrue(any("config.plist absent" in x for x in r["warnings"]))
 def test_config_requires_core_sections(self):
  with tempfile.TemporaryDirectory() as d:
   oc=Path(d)/"OC"; [ (oc/x).mkdir(parents=True) for x in ("ACPI","Kexts","Drivers","Resources","Tools") ]
   (oc/"compatibility-report.json").write_text(json.dumps({"status":"READY"}),encoding="utf-8")
   with (oc/"config.plist").open("wb") as f: plistlib.dump({},f)
   r=validate_opencore(d); self.assertEqual(r["status"],"FAIL"); self.assertTrue(any("PlatformInfo" in x for x in r["errors"]))
