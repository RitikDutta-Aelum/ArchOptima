#!/usr/bin/env python3
"""Validate portable bundle metadata, local resources, Python syntax and JSON; no execution."""
import argparse
import ast
import json
import re
from pathlib import Path

REQUIRED = ["SKILL.md", "agents/openai.yaml", "scripts/ingest.py", "scripts/optimize.py",
            "scripts/render_report.py", "scripts/allocate_costs.py", "scripts/install.py",
            "scripts/doctor.py", "scripts/check_report.py", "references/report-contract.md",
            "references/review-method.md", "references/document-intake.md", "references/cost-method.md",
            "references/servicenow.md", "references/research-context.md", "references/installation.md",
            "references/optimization-model.md", "assets/model.schema.json", "assets/architecture-report.md",
            "assets/decision-record.md", "examples/model.json", "examples/allocation.json"]


def reject_constant(value):raise ValueError(f"Nonfinite JSON constant: {value}")


def duplicate_keys(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError(f"Duplicate JSON key: {key}")
        result[key]=value
    return result


def validate(root):
    errors=[]
    for relative in REQUIRED:
        if not (root/relative).is_file():errors.append(f"Missing file: {relative}")
    if not (root/"SKILL.md").is_file():return errors
    text=(root/"SKILL.md").read_text(encoding="utf-8")
    front=re.match(r"\A---\n(.*?)\n---(?:\n|$)",text,re.S)
    if not front:errors.append("SKILL.md needs YAML frontmatter")
    else:
        values=dict(re.findall(r"^(name|description):[ \t]*(.+)$",front.group(1),re.M))
        if values.get("name")!="architecture-advisor":errors.append("Unexpected skill name")
        if not values.get("description"):errors.append("Description is required")
    if len(text.splitlines())>500:errors.append("SKILL.md exceeds 500 lines")
    if re.search(r"\[TODO|\{\{",text):errors.append("Unfinished SKILL.md placeholder")
    for raw_relative in set(re.findall(r"\b(?:references|assets|examples|scripts|evals)/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*",text)):
        relative = raw_relative.rstrip(".")
        resource = root/relative
        if not resource.resolve().is_relative_to(root.resolve()) or not resource.exists():
            errors.append(f"Broken resource reference: {relative}")
    for path in root.rglob("*"):
        if any(part in (".git","__pycache__",".venv") for part in path.relative_to(root).parts):continue
        if path.is_symlink():errors.append(f"Unexpected symlink: {path.relative_to(root)}")
        if not path.is_file():continue
        try:
            if path.suffix==".py":ast.parse(path.read_text(encoding="utf-8"),filename=str(path))
            if path.suffix==".json":json.loads(path.read_text(encoding="utf-8"),parse_constant=reject_constant,object_pairs_hook=duplicate_keys)
        except (SyntaxError,UnicodeError,ValueError) as exc:errors.append(f"{path.relative_to(root)}: {exc}")
    return errors


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir",type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args(argv)
    errors=validate(args.skill_dir)
    print(json.dumps({"passed":not errors,"errors":errors,"scope":"metadata, resources and syntax; use tests and review for behavior"},indent=2))
    return 1 if errors else 0

if __name__=="__main__":raise SystemExit(main())
