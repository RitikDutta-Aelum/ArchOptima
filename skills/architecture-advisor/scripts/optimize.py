#!/usr/bin/env python3
"""Solve a finite, reviewed architecture model. No network or AI calls.

Python 3.10+. Enumeration uses only the standard library. The explicit cp-sat
backend additionally requires OR-Tools. This does not implement the ETH paper.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import sys
import time
from typing import Any

VERSION = "1.0"
MAX_INPUT_BYTES = 5 * 1024 * 1024
SAFE_CP_INTEGER = 2**52 - 1
ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")


class ModelError(ValueError):
    """Input does not satisfy the supported model contract."""


class BackendError(RuntimeError):
    """An environment or backend failed; no mathematical conclusion follows."""


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ModelError(f"Duplicate JSON key: {key}")
        out[key] = value
    return out


def load_json(path: str | Path, *, max_bytes: int = MAX_INPUT_BYTES) -> dict[str, Any]:
    p = Path(path)
    with p.open("rb") as source:
        raw = source.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise ModelError(f"Input exceeds {max_bytes} bytes")
    try:
        value = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_pairs,
                           parse_constant=lambda s: (_ for _ in ()).throw(ModelError(f"Invalid JSON number: {s}")))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ModelError(f"Invalid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ModelError("The model must be a JSON object")
    return value


def _object(value: Any, where: str, required: set[str], optional: set[str] = frozenset()) -> None:
    if not isinstance(value, dict):
        raise ModelError(f"{where} must be an object")
    missing, extra = required - value.keys(), value.keys() - required - optional
    if missing:
        raise ModelError(f"{where} missing fields: {', '.join(sorted(missing))}")
    if extra:
        raise ModelError(f"{where} unsupported fields: {', '.join(sorted(extra))}")


def _text(value: Any, where: str, max_length: int = 4000) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > max_length:
        raise ModelError(f"{where} must be a nonempty string of at most {max_length} characters")


def _id(value: Any, where: str) -> None:
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise ModelError(f"{where} must match {ID.pattern}")


def _integer(value: Any, where: str, minimum: int | None = None) -> None:
    if type(value) is not int or (minimum is not None and value < minimum) or abs(value) > 10**18:
        raise ModelError(f"{where} must be an integer, not a boolean, within +/-10^18" +
                         (f", and >= {minimum}" if minimum is not None else ""))


def _list(value: Any, where: str, max_length: int, min_length: int = 0) -> None:
    if not isinstance(value, list) or not min_length <= len(value) <= max_length:
        raise ModelError(f"{where} must be a list with {min_length}..{max_length} items")


def _references(value: Any, where: str, known: set[str]) -> None:
    _list(value, where, 1000)
    if any(not isinstance(item, str) for item in value):
        raise ModelError(f"{where} must contain strings")
    if len(set(value)) != len(value):
        raise ModelError(f"{where} contains duplicate references")
    missing = set(value) - known
    if missing:
        raise ModelError(f"{where} references unknown IDs: {', '.join(sorted(missing))}")


def validate_model(model: dict[str, Any]) -> list[str]:
    """Strict structural validation; return evidence/completeness qualifications."""
    _object(model, "model", {"schema_version", "project", "metric_definitions", "decisions", "constraints"},
            {"evidence", "budget_total"})
    if model["schema_version"] != VERSION:
        raise ModelError("schema_version must be '1.0'")
    p = model["project"]
    _object(p, "project", {"name", "currency", "currency_scale", "horizon_months", "cost_basis", "cost_completeness"},
            {"assumptions"})
    _text(p["name"], "project.name", 300)
    if not isinstance(p["currency"], str) or not re.fullmatch(r"[A-Z]{3}", p["currency"]):
        raise ModelError("project.currency must be a three-letter uppercase currency code")
    if type(p["currency_scale"]) is not int or p["currency_scale"] not in {10**i for i in range(10)}:
        raise ModelError("project.currency_scale must be a power of ten from 1 through 1000000000")
    _integer(p["horizon_months"], "project.horizon_months", 1)
    if p["horizon_months"] > 1200:
        raise ModelError("project.horizon_months must be <= 1200")
    if p["cost_basis"] not in ("incremental", "total"):
        raise ModelError("project.cost_basis must be incremental or total")
    if p["cost_completeness"] not in ("complete", "partial"):
        raise ModelError("project.cost_completeness must be complete or partial")
    _list(p.get("assumptions", []), "project.assumptions", 100)
    for i, assumption in enumerate(p.get("assumptions", [])):
        _text(assumption, f"project.assumptions[{i}]")
    if "budget_total" in model:
        _integer(model["budget_total"], "budget_total", 0)
    metrics = model["metric_definitions"]
    if not isinstance(metrics, dict) or len(metrics) > 1000:
        raise ModelError("metric_definitions must be an object with at most 1000 metrics")
    for name, definition in metrics.items():
        _id(name, "metric ID")
        _object(definition, f"metric_definitions.{name}", {"unit", "description"})
        _text(definition["unit"], f"{name}.unit", 100)
        _text(definition["description"], f"{name}.description")
    evidence = model.get("evidence", [])
    _list(evidence, "evidence", 10000)
    evidence_ids: set[str] = set()
    for i, item in enumerate(evidence):
        _object(item, f"evidence[{i}]", {"id", "source", "locator"}, {"note"})
        _id(item["id"], f"evidence[{i}].id")
        if item["id"] in evidence_ids:
            raise ModelError(f"Duplicate evidence ID: {item['id']}")
        evidence_ids.add(item["id"])
        for key in ("source", "locator"):
            _text(item[key], f"evidence[{i}].{key}")
        if "note" in item:
            _text(item["note"], f"evidence[{i}].note")
    decisions = model["decisions"]
    _list(decisions, "decisions", 200, 1)
    decision_ids: set[str] = set()
    option_refs: set[str] = set()
    all_options: list[tuple[str, dict[str, Any]]] = []
    unsupported_evidence = 0
    for i, decision in enumerate(decisions):
        where = f"decisions[{i}]"
        _object(decision, where, {"id", "label", "options"})
        _id(decision["id"], where + ".id")
        _text(decision["label"], where + ".label", 300)
        if decision["id"] in decision_ids:
            raise ModelError(f"Duplicate decision ID: {decision['id']}")
        decision_ids.add(decision["id"])
        _list(decision["options"], where + ".options", 1000, 1)
        for j, option in enumerate(decision["options"]):
            loc = f"{where}.options[{j}]"
            _object(option, loc, {"id", "label", "one_time_cost", "monthly_cost", "metrics"},
                    {"requires", "incompatible_with", "evidence_ids"})
            _id(option["id"], loc + ".id")
            _text(option["label"], loc + ".label", 300)
            ref = decision["id"] + "." + option["id"]
            if ref in option_refs:
                raise ModelError(f"Duplicate option reference: {ref}")
            option_refs.add(ref)
            all_options.append((ref, option))
            _integer(option["one_time_cost"], loc + ".one_time_cost", 0)
            _integer(option["monthly_cost"], loc + ".monthly_cost", 0)
            if not isinstance(option["metrics"], dict):
                raise ModelError(loc + ".metrics must be an object")
            for key, value in option["metrics"].items():
                if key not in metrics:
                    raise ModelError(f"Unknown metric {key} in {ref}")
                _integer(value, f"{ref}.metrics.{key}")
            refs = option.get("evidence_ids", [])
            _references(refs, loc + ".evidence_ids", evidence_ids)
            unsupported_evidence += not refs
    if len(all_options) > 10000:
        raise ModelError("At most 10000 options are supported")
    for ref, option in all_options:
        for key in ("requires", "incompatible_with"):
            _references(option.get(key, []), ref + "." + key, option_refs)
    constraints = model["constraints"]
    _list(constraints, "constraints", 10000)
    constraint_ids: set[str] = set()
    for i, rule in enumerate(constraints):
        where = f"constraints[{i}]"
        _object(rule, where, {"id", "metric", "op", "value", "description"}, {"evidence_ids"})
        _id(rule["id"], where + ".id")
        if rule["id"] == "budget_total":
            raise ModelError("Constraint ID budget_total is reserved for the optional budget check")
        if rule["id"] in constraint_ids:
            raise ModelError(f"Duplicate constraint ID: {rule['id']}")
        constraint_ids.add(rule["id"])
        if not isinstance(rule["metric"], str) or rule["metric"] not in metrics:
            raise ModelError(f"{where}.metric references an unknown metric")
        if rule["op"] not in (">=", "<=", "=="):
            raise ModelError(f"{where}.op must be >=, <=, or ==")
        _integer(rule["value"], where + ".value")
        _text(rule["description"], where + ".description")
        _references(rule.get("evidence_ids", []), where + ".evidence_ids", evidence_ids)
        unsupported_evidence += not rule.get("evidence_ids")
    warnings = ["Results apply only to the listed choices, additive metrics, encoded constraints, and supplied estimates.",
                "Evidence references are retained, not authenticated or independently verified by this script.",
                "Missing option metrics contribute zero. This model does not infer throughput, latency, availability, or licensing."]
    if unsupported_evidence:
        warnings.append(f"{unsupported_evidence} option(s)/constraint(s) have no evidence references; treat their values as unverified assumptions.")
    if p["cost_completeness"] == "partial":
        warnings.append("Costs are declared partial. An optimal encoded objective is not a lowest-TCO recommendation.")
    else:
        warnings.append("Cost completeness is declared by the model author; the solver cannot verify that all real costs are included.")
    return warnings


def _passes(actual: int, op: str, target: int) -> bool:
    return actual >= target if op == ">=" else actual <= target if op == "<=" else actual == target


def evaluate_selection(model: dict[str, Any], option_ids: list[str]) -> dict[str, Any]:
    """Recalculate a full selection independently of the backend's constraint expressions."""
    if len(option_ids) != len(model["decisions"]):
        raise ModelError("Selection must contain exactly one option per decision")
    selected: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for decision, option_id in zip(model["decisions"], option_ids):
        matches = [o for o in decision["options"] if o["id"] == option_id]
        if len(matches) != 1:
            raise ModelError(f"Unknown selected option: {decision['id']}.{option_id}")
        selected.append((decision, matches[0]))
    refs = {d["id"] + "." + o["id"] for d, o in selected}
    sums = {metric: sum(o["metrics"].get(metric, 0) for _, o in selected)
            for metric in model["metric_definitions"]}
    one_time = sum(o["one_time_cost"] for _, o in selected)
    monthly = sum(o["monthly_cost"] for _, o in selected)
    total = one_time + model["project"]["horizon_months"] * monthly
    checks: list[dict[str, Any]] = []
    for rule in model["constraints"]:
        actual = sums[rule["metric"]]
        checks.append({"id": rule["id"], "description": rule["description"], "actual": actual,
                       "op": rule["op"], "required": rule["value"], "unit": model["metric_definitions"][rule["metric"]]["unit"],
                       "passed": _passes(actual, rule["op"], rule["value"]), "evidence_ids": rule.get("evidence_ids", [])})
    for d, o in selected:
        ref = d["id"] + "." + o["id"]
        for target in o.get("requires", []):
            checks.append({"id": f"{ref}:requires:{target}", "description": f"{ref} requires {target}", "passed": target in refs})
        for target in o.get("incompatible_with", []):
            checks.append({"id": f"{ref}:incompatible:{target}", "description": f"{ref} is incompatible with {target}", "passed": target not in refs})
    if "budget_total" in model:
        checks.append({"id": "budget_total", "description": "Whole-horizon budget", "actual": total, "op": "<=",
                       "required": model["budget_total"], "unit": "currency units", "passed": total <= model["budget_total"]})
    return {"selection": [{"decision_id": d["id"], "decision_label": d["label"], "option_id": o["id"],
                            "option_label": o["label"], "evidence_ids": o.get("evidence_ids", [])} for d, o in selected],
            "one_time_cost": one_time, "monthly_cost": monthly, "total_cost": total, "metrics": sums,
            "validation": {"passed": all(c["passed"] for c in checks), "checks": checks}}


def _key(solution: dict[str, Any]) -> tuple[Any, ...]:
    return (solution["total_cost"], tuple((s["decision_id"], s["option_id"]) for s in solution["selection"]))


def _enumerate(model: dict[str, Any], start: float, time_limit: float, max_states: int, top_k: int) -> dict[str, Any]:
    total = math.prod(len(d["options"]) for d in model["decisions"])
    evaluated = feasible = 0
    candidates: list[dict[str, Any]] = []
    reason = "exhausted"
    for combination in itertools.product(*[[o["id"] for o in d["options"]] for d in model["decisions"]]):
        if evaluated >= max_states:
            reason = "state_limit"
            break
        if time.monotonic() - start >= time_limit:
            reason = "time_limit"
            break
        solution = evaluate_selection(model, list(combination))
        evaluated += 1
        if solution["validation"]["passed"]:
            feasible += 1
            candidates.append(solution)
            candidates.sort(key=_key)
            del candidates[top_k:]
    complete = evaluated == total
    status = ("OPTIMAL" if candidates else "INFEASIBLE") if complete else ("FEASIBLE" if candidates else "UNKNOWN")
    bound = candidates[0]["total_cost"] if status == "OPTIMAL" else 0 if candidates else None
    return {"status": status, "candidates": candidates, "best_bound": bound,
            "search": {"total_combinations": total, "evaluated_states": evaluated, "feasible_states": feasible,
                       "complete": complete, "stop_reason": "exhausted" if complete else reason,
                       "alternatives_complete": complete}}


def _cp_sat(model: dict[str, Any], start: float, time_limit: float, top_k: int) -> dict[str, Any]:
    try:
        from ortools.sat.python import cp_model
    except ImportError as exc:
        raise BackendError("OR-Tools is not installed. Use --backend enumerate or install the documented optional dependency.") from exc
    cp = cp_model.CpModel()
    variables = {}
    option_pairs = []
    horizon = model["project"]["horizon_months"]
    for decision in model["decisions"]:
        group = []
        for option in decision["options"]:
            ref = decision["id"] + "." + option["id"]
            var = cp.new_bool_var(ref)
            variables[ref] = var
            option_pairs.append((ref, option))
            group.append(var)
        cp.add(sum(group) == 1)
    # Bound integer expressions so the floating objective bound can be reported
    # conservatively without losing whole currency-unit precision.
    coefficients = [o["one_time_cost"] + horizon * o["monthly_cost"] for _, o in option_pairs]
    if sum(abs(c) for c in coefficients) > SAFE_CP_INTEGER:
        raise BackendError("CP-SAT cost expression exceeds the supported safe range; rescale or use enumeration")
    for metric in model["metric_definitions"]:
        if sum(abs(o["metrics"].get(metric, 0)) for _, o in option_pairs) > SAFE_CP_INTEGER:
            raise BackendError(f"CP-SAT metric expression {metric} exceeds the supported safe range")
    for rule in model["constraints"]:
        if abs(rule["value"]) > SAFE_CP_INTEGER:
            raise BackendError("CP-SAT constraint value exceeds the supported safe range")
        expression = sum(o["metrics"].get(rule["metric"], 0) * variables[ref] for ref, o in option_pairs)
        cp.add(expression >= rule["value"] if rule["op"] == ">=" else
               expression <= rule["value"] if rule["op"] == "<=" else expression == rule["value"])
    for ref, option in option_pairs:
        for target in option.get("requires", []):
            cp.add(variables[ref] <= variables[target])
        for target in option.get("incompatible_with", []):
            cp.add(variables[ref] + variables[target] <= 1)
    objective = sum(c * variables[ref] for c, (ref, _) in zip(coefficients, option_pairs))
    if "budget_total" in model:
        if model["budget_total"] > SAFE_CP_INTEGER:
            raise BackendError("CP-SAT budget exceeds the supported safe range")
        cp.add(objective <= model["budget_total"])
    cp.minimize(objective)
    invalid = cp.validate()
    if invalid:
        raise BackendError("CP-SAT rejected the generated model: " + invalid)
    candidates = []
    first_status = "UNKNOWN"
    first_bound = None
    branches = 0
    alternatives_complete = True
    reason = "top_k_reached"
    for iteration in range(top_k):
        remaining = time_limit - (time.monotonic() - start)
        if remaining <= 0:
            reason, alternatives_complete = "time_limit", False
            break
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = remaining
        solver.parameters.num_search_workers = 1
        solver.parameters.random_seed = 0
        code = solver.solve(cp)
        branches += solver.num_branches
        status = {cp_model.OPTIMAL: "OPTIMAL", cp_model.FEASIBLE: "FEASIBLE",
                  cp_model.INFEASIBLE: "INFEASIBLE", cp_model.UNKNOWN: "UNKNOWN",
                  cp_model.MODEL_INVALID: "MODEL_INVALID"}.get(code, "UNKNOWN")
        if iteration == 0:
            first_status = status
        if status not in ("OPTIMAL", "FEASIBLE"):
            if status == "MODEL_INVALID":
                raise BackendError("CP-SAT returned MODEL_INVALID for the generated model")
            reason = "remaining_infeasible" if status == "INFEASIBLE" else "time_limit_or_solver_stop"
            alternatives_complete = status == "INFEASIBLE"
            break
        choices = []
        chosen_variables = []
        for decision in model["decisions"]:
            selected = [o["id"] for o in decision["options"] if solver.value(variables[decision["id"] + "." + o["id"]])]
            if len(selected) != 1:
                raise BackendError("Backend returned an invalid selection")
            choices.append(selected[0])
            chosen_variables.append(variables[decision["id"] + "." + selected[0]])
        checked = evaluate_selection(model, choices)
        if not checked["validation"]["passed"]:
            raise BackendError("Backend solution failed independent constraint evaluation")
        candidates.append(checked)
        if iteration == 0:
            first_bound = checked["total_cost"] if status == "OPTIMAL" else max(0, math.floor(solver.best_objective_bound))
        if status != "OPTIMAL":
            reason, alternatives_complete = "time_limit_or_solver_stop", False
            break
        cp.add(sum(chosen_variables) <= len(chosen_variables) - 1)
    candidates.sort(key=_key)
    return {"status": first_status, "candidates": candidates, "best_bound": first_bound,
            "search": {"total_combinations": math.prod(len(d["options"]) for d in model["decisions"]),
                       "evaluated_states": None, "feasible_states": None, "solver_branches": branches,
                       "complete": first_status in ("OPTIMAL", "INFEASIBLE"), "stop_reason": reason,
                       "alternatives_complete": alternatives_complete}}


def solve(model: dict[str, Any], *, backend: str = "enumerate", time_limit: float = 30.0,
          max_states: int = 100000, top_k: int = 3) -> dict[str, Any]:
    warnings = validate_model(model)
    if type(time_limit) not in (float, int) or not math.isfinite(time_limit) or time_limit < 0:
        raise ModelError("time_limit must be a finite nonnegative number")
    if type(max_states) is not int or max_states < 0:
        raise ModelError("max_states must be a nonnegative integer")
    if type(top_k) is not int or not 1 <= top_k <= 20:
        raise ModelError("top_k must be an integer between 1 and 20")
    if backend not in ("enumerate", "cp-sat"):
        raise ModelError("backend must be enumerate or cp-sat")
    start = time.monotonic()
    data = (_enumerate(model, start, time_limit, max_states, top_k) if backend == "enumerate" else
            _cp_sat(model, start, time_limit, top_k))
    elapsed = time.monotonic() - start
    candidates = data.pop("candidates")
    best = candidates[0] if candidates else None
    best_bound = data.pop("best_bound")
    if best and (not best["validation"]["passed"] or best_bound is not None and best_bound > best["total_cost"]):
        raise BackendError("Internal result validation failed")
    if backend == "cp-sat":
        warnings.append("max_states is an enumeration-only limit. CP-SAT uses the wall-time limit; candidate counts are not model counts.")
    if data["status"] == "OPTIMAL":
        interpretation = ("Minimum modeled cost among the listed feasible combinations; real-world validity depends on the model and evidence."
                          if model["project"]["cost_completeness"] == "complete" else
                          "Minimum of the encoded partial-cost objective only; no lowest-TCO claim is supported.")
    elif data["status"] == "FEASIBLE":
        interpretation = "A valid modeled combination was found. It is the best retained candidate, with no proven optimality."
    elif data["status"] == "INFEASIBLE":
        interpretation = "No listed combination satisfies the encoded constraints. This does not exclude unmodeled designs."
    else:
        interpretation = "No conclusion about feasibility was established within the search limits."
    return {"run_schema_version": VERSION, "model_sha256": hashlib.sha256(json.dumps(model, sort_keys=True, separators=(",", ":"),
                                                                                           ensure_ascii=False).encode("utf-8")).hexdigest(),
            "backend": backend, **data, "elapsed_seconds": round(elapsed, 6), "interpretation": interpretation,
            "limits": {"time_seconds": time_limit, "max_states": max_states, "top_k": top_k},
            "objective": {"kind": "minimum_horizon_cost", "best_value": best["total_cost"] if best else None,
                          "best_bound": best_bound,
                          "absolute_gap": best["total_cost"] - best_bound if best and best_bound is not None else None},
            "best_solution": best, "alternatives": candidates[1:], "warnings": warnings, "model_snapshot": model}


def write_output(path: str | Path, data: str) -> None:
    """Never silently replace an earlier run."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8", newline="\n") as output:
        output.write(data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", help="Reviewed JSON model")
    parser.add_argument("--output", required=True, help="New JSON output file; existing files are refused")
    parser.add_argument("--backend", choices=("enumerate", "cp-sat"), default="enumerate")
    parser.add_argument("--time-limit", type=float, default=30.0)
    parser.add_argument("--max-states", type=int, default=100000, help="Enumeration limit only")
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args(argv)
    exit_code = 0
    try:
        result = solve(load_json(args.model), backend=args.backend, time_limit=args.time_limit,
                       max_states=args.max_states, top_k=args.top_k)
    except ModelError as exc:
        result = {"run_schema_version": VERSION, "status": "MODEL_INVALID", "error": str(exc)}
        exit_code = 2
    except (BackendError, OSError) as exc:
        result = {"run_schema_version": VERSION, "status": "ERROR", "error": str(exc)}
        exit_code = 3
    try:
        write_output(args.output, json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    except OSError as exc:
        print(f"Could not create output: {exc}", file=sys.stderr)
        return 3
    print(json.dumps({"status": result["status"], "output": str(Path(args.output)),
                      "best_value": result.get("objective", {}).get("best_value")}))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
