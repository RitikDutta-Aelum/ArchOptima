#!/usr/bin/env python3
"""Render a local optimizer run into a factual Markdown calculation appendix.

This is not a full architecture assessment. It does not invent evidence,
reliability predictions, recommendations, or business savings.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from optimize import ModelError, evaluate_selection, load_json, validate_model, write_output

MAX_RUN_BYTES = 32 * 1024 * 1024


def esc(value: Any) -> str:
    text = str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    for ch in ("\\", "`", "*", "_", "[", "]", "|", "#"):
        text = text.replace(ch, "\\" + ch)
    return text.replace("\r", " ").replace("\n", " ")


def money(value: int | None, project: dict[str, Any]) -> str:
    if value is None:
        return "Not established"
    places = len(str(project["currency_scale"])) - 1
    amount = Decimal(value) / Decimal(project["currency_scale"])
    return f"{project['currency']} {amount:,.{places}f}"


def render(run: dict[str, Any]) -> str:
    if run.get("run_schema_version") != "1.0":
        raise ModelError("Unsupported run_schema_version")
    status = run.get("status")
    if status not in {"OPTIMAL", "FEASIBLE", "INFEASIBLE", "UNKNOWN", "MODEL_INVALID", "ERROR"}:
        raise ModelError("Unknown run status")
    if status in {"MODEL_INVALID", "ERROR"}:
        return ("# Architecture Optimization Run\n\n"
                "**Calculation appendix only. No architecture recommendation was established.**\n\n"
                f"**Status:** {status}\n\n**Issue:** {esc(run.get('error', 'Unspecified error'))}\n")
    model = run.get("model_snapshot")
    validate_model(model)
    digest = hashlib.sha256(json.dumps(model, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
    if digest != run.get("model_sha256"):
        raise ModelError("Run model hash does not match its snapshot")
    project = model["project"]
    best = run.get("best_solution")
    alternatives = run.get("alternatives", [])
    if not isinstance(alternatives, list):
        raise ModelError("Run alternatives must be a list")
    if status in {"OPTIMAL", "FEASIBLE"} and not best:
        raise ModelError("A successful run requires a solution")
    if status in {"INFEASIBLE", "UNKNOWN"} and (best or alternatives):
        raise ModelError("Run status contradicts its solutions")
    for candidate in ([best] if best else []) + alternatives:
        try:
            selection = candidate["selection"]
            if [s["decision_id"] for s in selection] != [d["id"] for d in model["decisions"]]:
                raise ModelError("Candidate decision order does not match the model")
            checked = evaluate_selection(model, [s["option_id"] for s in selection])
            if not checked["validation"]["passed"] or checked != candidate:
                raise ModelError("Stored candidate does not match independently recalculated costs and constraints")
        except (KeyError, TypeError) as exc:
            raise ModelError("Malformed stored candidate") from exc
    objective = run.get("objective", {})
    if not isinstance(objective, dict):
        raise ModelError("Run objective must be an object")
    if best and objective.get("best_value") != best["total_cost"]:
        raise ModelError("Run objective disagrees with its best solution")
    if status == "OPTIMAL" and objective.get("best_bound") != objective.get("best_value"):
        raise ModelError("An optimal result must have an equal recorded bound and objective")
    search = run.get("search", {})
    if not isinstance(search, dict):
        raise ModelError("Run search must be an object")
    if not isinstance(run.get("warnings", []), list) or any(not isinstance(w, str) for w in run.get("warnings", [])):
        raise ModelError("Run warnings must be a list of strings")
    if status in {"OPTIMAL", "INFEASIBLE"} and not search.get("complete"):
        raise ModelError("A conclusive status requires a completed proof/search flag")
    lines = [f"# Architecture Optimization Run: {esc(project['name'])}", "",
             "**Calculation appendix only. This report checks a supplied mathematical model; it is not a full architectural assessment.**", "",
             "## Decision status", "",
             f"**Status:** {status}  ", f"**Interpretation:** {esc(run['interpretation'])}", "",
             "| Run field | Value |", "| --- | --- |",
             f"| Backend | {esc(run['backend'])} |",
             f"| Planning horizon | {project['horizon_months']} months |",
             f"| Cost basis | {esc(project['cost_basis'])} |",
             f"| Cost completeness | {esc(project['cost_completeness'])}, as declared by the model author |",
             f"| Objective | {money(objective.get('best_value'), project)} |",
             f"| Recorded lower bound | {money(objective.get('best_bound'), project)} |",
             f"| Absolute objective gap | {money(objective.get('absolute_gap'), project)} |",
             f"| Elapsed search time | {esc(run['elapsed_seconds'])} seconds |",
             f"| Total possible combinations | {esc(search.get('total_combinations', 'Unknown'))} |",
             f"| Enumerated complete assignments | {esc(search.get('evaluated_states') if search.get('evaluated_states') is not None else 'Not reported by this backend')} |",
             f"| Stop reason | {esc(search.get('stop_reason', 'Unknown'))} |", ""]
    if best:
        lines += ["## Selected modeled design", "", "| Decision | Selected option | Evidence references |", "| --- | --- | --- |"]
        for item in best["selection"]:
            lines.append(f"| {esc(item['decision_label'])} | {esc(item['option_label'])} | {esc(', '.join(item['evidence_ids']) or 'None supplied')} |")
        lines += ["", "### Cost calculation", "",
                  f"- One-time cost: **{money(best['one_time_cost'], project)}**.",
                  f"- Monthly recurring cost: **{money(best['monthly_cost'], project)}**.",
                  f"- {project['horizon_months']}-month modeled total: **{money(best['total_cost'], project)}**.", "",
                  "The calculation is one-time cost plus horizon months multiplied by the monthly cost. It does not add discounting, taxes, growth, contract changes, or costs absent from the input.", "",
                  "### Constraint validation", "", "| Constraint | Result | Calculation |", "| --- | --- | --- |"]
        for check in best["validation"]["checks"]:
            calculation = f"{check['actual']} {check['op']} {check['required']} {check['unit']}" if "actual" in check else check["description"]
            lines.append(f"| {esc(check['id'])}: {esc(check['description'])} | {'PASS' if check['passed'] else 'FAIL'} | {esc(calculation)} |")
        if not best["validation"]["checks"]:
            lines.append("| No explicit constraints supplied | Not assessed | Only selection and cost rules were applied |")
        lines += ["", "## Retained alternatives", ""]
        if alternatives:
            lines += ["| Alternative choices | Modeled total | Difference from selected design |", "| --- | --- | --- |"]
            for item in alternatives:
                labels = "; ".join(s["option_label"] for s in item["selection"])
                lines.append(f"| {esc(labels)} | {money(item['total_cost'], project)} | {money(item['total_cost'] - best['total_cost'], project)} |")
            lines += ["", "Cost differences compare supplied candidate estimates; they are not realized savings or differences from an independently established baseline."]
        else:
            lines.append("No additional candidates were retained. This does not imply that no other feasible designs exist.")
        lines += ["", "Alternatives are retained by modeled cost. No Pareto frontier, risk score, or diversity guarantee is implied.", ""]
    else:
        lines += ["## Result", "", "No feasible selection is included in this run. Review the status before concluding that requirements conflict.", ""]
    lines += ["## Assumptions and limits", ""]
    for item in project.get("assumptions", []):
        lines.append("- " + esc(item))
    for item in run.get("warnings", []):
        lines.append("- " + esc(item))
    lines += ["- This renderer recalculates returned selections, costs, and constraints. It does not independently re-prove the solver's optimality or infeasibility claim.",
              "", "## Evidence register", "", "| ID | Source | Locator | Note |", "| --- | --- | --- | --- |"]
    for item in model.get("evidence", []):
        lines.append(f"| {esc(item['id'])} | {esc(item['source'])} | {esc(item['locator'])} | {esc(item.get('note', ''))} |")
    if not model.get("evidence"):
        lines.append("| None | No sources supplied | Not available | Treat all inputs as unverified assumptions |")
    lines += ["", "## Traceability", "", f"Model SHA-256: `{digest}`", "",
              "Retain this report with its run JSON and reviewed source files. Architect review is required to assess omitted constraints, evidence quality, and implementation implications.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", help="Optimizer run JSON")
    parser.add_argument("--output", required=True, help="New Markdown output file; existing files are refused")
    args = parser.parse_args(argv)
    try:
        report = render(load_json(args.run, max_bytes=MAX_RUN_BYTES))
        write_output(args.output, report)
    except (ModelError, OSError, KeyError, TypeError, ValueError) as exc:
        print(f"Could not render report: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"output": str(Path(args.output))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
