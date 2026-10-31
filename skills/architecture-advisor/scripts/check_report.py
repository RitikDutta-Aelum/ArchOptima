#!/usr/bin/env python3
"""Check full-format architecture report structure; does not verify evidence or facts."""
import argparse
import json
import re
from pathlib import Path

HEADINGS = ("Executive decision", "Scope and evidence", "Architecture assessment",
            "Requirements and constraints", "Options and trade-offs", "Cost and resource analysis",
            "Risks and verification", "Recommended actions", "Decision record", "Sources and limitations")


def check(text):
    errors, warnings = [], []
    found = {re.sub(r"^\d+[.)]\s*", "", m.group(1)).strip().casefold()
             for m in re.finditer(r"^##\s+(.+)$", text, flags=re.M)}
    for heading in HEADINGS:
        if heading.casefold() not in found:errors.append(f"Missing section: {heading}")
    if re.search(r"\{\{[^}]+\}\}|<INSERT[^>]*>|\[TODO\]", text, re.I):
        errors.append("Unresolved template placeholder")
    if not re.search(r"Decision status\*{0,2}:", text, re.I):
        errors.append("Missing explicit Decision status label")
    for part in re.split(r"^##\s+", text, flags=re.M)[1:]:
        heading, _, body=part.partition("\n")
        if not body.strip():errors.append(f"Empty section: {heading.strip()}")
    if not re.search(r"\bE-[A-Za-z0-9_-]+|https?://|\b(?:page|slide|sheet|line|p\.)\s*\d", text, re.I):
        warnings.append("No recognizable evidence locator; manually check material claims")
    return {"check_type":"structure_only", "passed":not errors, "errors":errors,"warnings":warnings,
            "limitations":["This check does not establish citation accuracy, mathematical correctness, completeness or usefulness.",
                           "Use only for the full report template, not short answers or mathematical run reports."]}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report",type=Path)
    args=parser.parse_args(argv)
    try:
        if args.report.stat().st_size>5*1024*1024:raise ValueError("Report exceeds 5 MiB")
        result=check(args.report.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:parser.exit(2,f"Report check failed: {exc}\n")
    print(json.dumps(result,indent=2))
    return 0 if result["passed"] else 1

if __name__=="__main__":raise SystemExit(main())
