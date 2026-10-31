#!/usr/bin/env python3
"""Report local optional capabilities; install nothing and contact no services."""
import argparse
import importlib.util
import json
import platform
import shutil
import sys
from pathlib import Path


def inspect():
    packages = {name: importlib.util.find_spec(name) is not None
                for name in ("pypdf", "PIL", "openpyxl", "ortools")}
    return {"python": platform.python_version(), "python_supported": sys.version_info >= (3,10),
            "skill_root": str(Path(__file__).resolve().parents[1]), "optional_packages": packages,
            "optional_commands": {name: bool(shutil.which(name)) for name in ("pdftoppm", "tesseract")},
            "capabilities": {"text_office_xml_csv": True, "exact_bounded_enumeration": True,
                             "cost_allocation": True, "pdf_text": packages["pypdf"],
                             "image_metadata": packages["PIL"], "xlsx": packages["openpyxl"],
                             "cp_sat": packages["ortools"]},
            "notes": ["Package presence is a capability hint, not an end-to-end runtime test.",
                      "Vision, browsing, file uploads and tool permissions are supplied by the host.",
                      "The intake helper does not perform OCR or claim visual understanding.",
                      "No API key is required by these local scripts."]}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args=parser.parse_args(argv)
    result=inspect()
    if args.json: print(json.dumps(result,indent=2))
    else:
        print("Architecture Advisor local capability check")
        print("Python:",result["python"],"(supported)" if result["python_supported"] else "(requires 3.10+)")
        for name,ready in result["capabilities"].items(): print(f"  {name}: {'available' if ready else 'optional dependency absent'}")
        for note in result["notes"]:print("Note:",note)
    return 0 if result["python_supported"] else 1

if __name__=="__main__":raise SystemExit(main())
