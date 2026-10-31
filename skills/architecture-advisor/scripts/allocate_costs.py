#!/usr/bin/env python3
"""Allocate integer monetary units exactly; no network calls or invoice changes."""
from __future__ import annotations
import argparse
import json
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path


def integer(value, label, minimum=0):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{label} must be an integer >= {minimum}")
    return value


def identity(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def allocate(model):
    if not isinstance(model, dict) or model.get("schema_version") != "1.0":
        raise ValueError("Expected an object with schema_version 1.0")
    currency = identity(model.get("currency"), "currency")
    scale = integer(model.get("currency_scale", 1), "currency_scale", 1)
    if scale not in (1, 10, 100, 1000, 10000):
        raise ValueError("currency_scale must be 1, 10, 100, 1000, or 10000")
    period = identity(model.get("period"), "period")
    apps = model.get("applications")
    pools = model.get("shared_pools", [])
    if not isinstance(apps, list) or not apps or not isinstance(pools, list):
        raise ValueError("applications must be nonempty and shared_pools must be a list")
    if len(apps) > 10000 or len(pools) > 10000:
        raise ValueError("Maximum 10000 applications or pools")
    rows = {}
    for app in apps:
        if not isinstance(app, dict):
            raise ValueError("Each application must be an object")
        key = identity(app.get("id"), "application id")
        if key in rows:
            raise ValueError(f"Duplicate application id: {key}")
        rows[key] = {"id": key, "label": identity(app.get("label", key), "application label"),
                     "direct_cost": integer(app.get("direct_cost", 0), f"{key}.direct_cost"),
                     "allocated_shared_cost": 0}
    pool_results, pool_ids, unallocated = [], set(), 0
    for pool in pools:
        if not isinstance(pool, dict):
            raise ValueError("Each shared pool must be an object")
        key = identity(pool.get("id"), "pool id")
        if key in pool_ids:
            raise ValueError(f"Duplicate pool id: {key}")
        pool_ids.add(key)
        cost = integer(pool.get("cost"), f"{key}.cost")
        basis = identity(pool.get("allocation_basis"), f"{key}.allocation_basis")
        weights = pool.get("weights", {})
        if not isinstance(weights, dict) or set(weights) - set(rows):
            raise ValueError(f"{key}.weights contains unknown applications or is not an object")
        exact = {}
        for app_id in rows:
            raw = weights.get(app_id, 0)
            if isinstance(raw, bool) or not isinstance(raw, (str, int, Decimal)):
                raise ValueError(f"{key}.{app_id} weight must be an integer or decimal string")
            try:
                value = Decimal(raw)
            except (InvalidOperation, ValueError):
                raise ValueError(f"{key}.{app_id} has an invalid weight") from None
            if not value.is_finite() or value < 0:
                raise ValueError(f"{key}.{app_id} weight must be finite and nonnegative")
            if len(value.as_tuple().digits) > 100 or abs(value.as_tuple().exponent) > 100:
                raise ValueError("Weight precision/exponent exceeds the supported bound")
            exact[app_id] = Fraction(value)
        total_weight = sum(exact.values(), Fraction(0))
        amounts = {app_id: 0 for app_id in rows}
        remainder = cost
        if total_weight:
            shares = {app_id: cost * value / total_weight for app_id, value in exact.items()}
            amounts = {app_id: value.numerator // value.denominator for app_id, value in shares.items()}
            missing_units = cost - sum(amounts.values())
            ranked = sorted(rows, key=lambda app_id: (-(shares[app_id] - amounts[app_id]), app_id))
            for app_id in ranked[:missing_units]:
                amounts[app_id] += 1
            remainder = 0
        for app_id, amount in amounts.items():
            rows[app_id]["allocated_shared_cost"] += amount
        unallocated += remainder
        pool_results.append({"id": key, "cost": cost, "allocation_basis": basis,
                             "weights": {k: str(weights.get(k, 0)) for k in rows},
                             "allocations": amounts, "unallocated_cost": remainder})
    app_results = []
    for row in rows.values():
        app_results.append(dict(row, total_allocated_cost=row["direct_cost"] + row["allocated_shared_cost"]))
    direct = sum(row["direct_cost"] for row in app_results)
    shared = sum(pool["cost"] for pool in pool_results)
    allocated = sum(row["total_allocated_cost"] for row in app_results)
    assert allocated + unallocated == direct + shared
    return {"schema_version": "1.0", "report_type": "cost_allocation", "currency": currency,
            "currency_scale": scale, "period": period, "method": "largest_remainder_integer_units",
            "applications": app_results, "shared_pools": pool_results,
            "totals": {"direct_cost": direct, "shared_cost": shared,
                       "allocated_cost": allocated, "unallocated_cost": unallocated,
                       "source_total_cost": direct + shared, "reconciled": True},
            "limitations": ["Allocation redistributes the supplied costs; it does not establish a saving.",
                            "The user supplies the allocation policy, period, currency and evidence.",
                            "Negative costs/credits and cross-currency conversion are not supported."]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.model.stat().st_size > 10 * 1024 * 1024:
            raise ValueError("Input exceeds 10 MiB")
        model = json.loads(args.model.read_text(encoding="utf-8-sig"),
                           parse_float=Decimal, object_pairs_hook=unique_pairs)
        result = allocate(model)
        text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(text)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Allocation failed: {exc}\n")
    print(f"Allocated {result['totals']['allocated_cost']} integer units; "
          f"unallocated {result['totals']['unallocated_cost']}; totals reconcile.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
