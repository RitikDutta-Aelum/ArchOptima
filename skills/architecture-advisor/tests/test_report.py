import importlib.util
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("reportcheck",ROOT/"scripts"/"check_report.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ReportTests(unittest.TestCase):
    def report(self):return "# Review\n**Decision status:** Conditional recommendation\n"+"\n".join(f"## {i}. {h}\nEvidence E-test-1. Specific finding.\n" for i,h in enumerate(m.HEADINGS,1))
    def test_complete_structure(self):self.assertTrue(m.check(self.report())["passed"])
    def test_template_rejected(self):self.assertFalse(m.check(self.report()+"{{PROJECT}}")["passed"])
    def test_missing_section(self):self.assertFalse(m.check(self.report().replace("## 8. Recommended actions","## 8. Something else"))["passed"])
    def test_empty_section(self):self.assertFalse(m.check(self.report()+"\n## Empty\n")["passed"])
if __name__=="__main__":unittest.main()
