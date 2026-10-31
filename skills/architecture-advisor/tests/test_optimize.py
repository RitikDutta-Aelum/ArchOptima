"""Meaningful correctness/status tests; no external services or private data."""
from __future__ import annotations

from contextlib import redirect_stdout
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import optimize
import render_report


def example():
    return json.loads((ROOT / "examples" / "model.json").read_text())


def resource_model():
    model = example()
    model["metric_definitions"] = {"remaining_capacity": {"unit": "jobs/min", "description": "Supply minus demand"}}
    model["decisions"] = [
        {"id": "pool", "label": "Shared pool", "options": [
            {"id": "off", "label": "Off", "one_time_cost": 0, "monthly_cost": 0, "metrics": {}},
            {"id": "on", "label": "On", "one_time_cost": 100, "monthly_cost": 10,
             "metrics": {"remaining_capacity": 100}},
        ]},
        {"id": "appA", "label": "Application A", "options": [
            {"id": "pool", "label": "Shared", "one_time_cost": 1, "monthly_cost": 0,
             "metrics": {"remaining_capacity": -60}, "requires": ["pool.on"]},
            {"id": "own", "label": "Dedicated", "one_time_cost": 200, "monthly_cost": 10, "metrics": {}},
        ]},
        {"id": "appB", "label": "Application B", "options": [
            {"id": "pool", "label": "Shared", "one_time_cost": 1, "monthly_cost": 0,
             "metrics": {"remaining_capacity": -60}, "requires": ["pool.on"]},
            {"id": "own", "label": "Dedicated", "one_time_cost": 250, "monthly_cost": 10, "metrics": {}},
        ]},
    ]
    model["constraints"] = [{"id": "capacity", "metric": "remaining_capacity", "op": ">=", "value": 0,
                              "description": "Combined demand cannot exceed pool capacity"}]
    return model


class OptimizationTests(unittest.TestCase):
    def test_known_cost_and_constraint_results(self):
        result = optimize.solve(example())
        self.assertEqual(result["status"], "OPTIMAL")
        self.assertEqual(result["objective"]["best_value"], 3130000)
        self.assertEqual(result["objective"]["absolute_gap"], 0)
        self.assertEqual(result["best_solution"]["selection"][0]["option_id"], "shared_redundant")
        self.assertEqual(result["alternatives"][0]["total_cost"], 3770000)
        self.assertEqual(result["search"]["evaluated_states"], 3)

    def test_demand_changes_architecture(self):
        model = example()
        model["constraints"][0]["value"] = 150
        result = optimize.solve(model)
        self.assertEqual(result["objective"]["best_value"], 3770000)
        self.assertEqual(result["best_solution"]["selection"][0]["option_id"], "dedicated_redundant")

    def test_conflicting_requirements_proven_infeasible(self):
        model = example()
        model["constraints"].append({"id": "maximum", "metric": "capacity_jobs_per_min", "op": "<=", "value": 99,
                                     "description": "Deliberately incompatible with the minimum capacity"})
        result = optimize.solve(model)
        self.assertEqual(result["status"], "INFEASIBLE")
        self.assertTrue(result["search"]["complete"])
        self.assertIsNone(result["best_solution"])

    def test_limit_with_no_incumbent_is_unknown(self):
        result = optimize.solve(example(), max_states=1)
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertFalse(result["search"]["complete"])
        self.assertEqual(result["search"]["stop_reason"], "state_limit")

    def test_limit_with_incumbent_is_feasible(self):
        result = optimize.solve(example(), max_states=2)
        self.assertEqual(result["status"], "FEASIBLE")
        self.assertEqual(result["objective"]["best_value"], 3130000)
        self.assertEqual(result["objective"]["best_bound"], 0)

    def test_limit_equal_to_search_size_is_complete(self):
        result = optimize.solve(example(), max_states=3)
        self.assertEqual(result["status"], "OPTIMAL")

    def test_zero_time_does_not_mean_infeasible(self):
        result = optimize.solve(example(), time_limit=0)
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertEqual(result["search"]["evaluated_states"], 0)

    def test_budget_applies_to_whole_horizon(self):
        model = example()
        model["budget_total"] = 3130000
        self.assertEqual(optimize.solve(model)["status"], "OPTIMAL")
        model["budget_total"] = 3129999
        self.assertEqual(optimize.solve(model)["status"], "INFEASIBLE")

    def test_shared_cost_capacity_and_dependencies(self):
        # Independent manual comparison: sharing both exceeds capacity; keeping
        # both dedicated costs 930; pool+A-dedicated+B-shared costs 781;
        # pool+A-shared+B-dedicated costs 831. Fixed pool cost appears once.
        result = optimize.solve(resource_model(), top_k=5)
        self.assertEqual(result["objective"]["best_value"], 781)
        self.assertEqual([s["option_id"] for s in result["best_solution"]["selection"]], ["on", "own", "pool"])
        self.assertEqual(result["best_solution"]["metrics"]["remaining_capacity"], 40)

    def test_incompatibility_removes_a_selected_pair(self):
        model = resource_model()
        model["decisions"][2]["options"][0]["incompatible_with"] = ["appA.own"]
        result = optimize.solve(model)
        self.assertEqual(result["objective"]["best_value"], 831)

    def test_currency_units_are_exact(self):
        model = example()
        model["project"]["currency_scale"] = 100
        model["project"]["horizon_months"] = 3
        model["decisions"][0]["options"] = [model["decisions"][0]["options"][1]]
        model["decisions"][0]["options"][0].update(one_time_cost=1, monthly_cost=2)
        result = optimize.solve(model)
        self.assertEqual(result["objective"]["best_value"], 7)
        self.assertIn("INR 0.07", render_report.render(result))

    def test_enumeration_does_not_round_large_integer_costs(self):
        model = example()
        model["decisions"][0]["options"] = model["decisions"][0]["options"][1:]
        for index, option in enumerate(model["decisions"][0]["options"]):
            option.update(one_time_cost=10**18-index, monthly_cost=0)
        result = optimize.solve(model)
        self.assertEqual(result["objective"]["best_value"], 10**18 - 1)
        self.assertEqual(result["best_solution"]["selection"][0]["option_id"], "dedicated_redundant")

    def test_partial_costs_are_not_lowest_tco(self):
        model = example()
        model["project"]["cost_completeness"] = "partial"
        result = optimize.solve(model)
        self.assertEqual(result["status"], "OPTIMAL")
        self.assertIn("no lowest-TCO claim", result["interpretation"])

    def test_model_validation_rejects_wrong_types_unknowns_and_duplicates(self):
        mutations = [
            lambda m: m["project"].update(currency_scale=True),
            lambda m: m["project"].update(horizon_months=24.0),
            lambda m: m["decisions"][0]["options"][0].update(monthly_cost=True),
            lambda m: m["decisions"][0]["options"][0].update(monthly_cost=float("nan")),
            lambda m: m["decisions"][0]["options"][0].update(requires=["processing.missing"]),
            lambda m: m["decisions"][0]["options"][0].update(evidence_ids=["E-missing"]),
            lambda m: m["constraints"][0].update(op=">"),
            lambda m: m["constraints"][0].update(metric="missing"),
            lambda m: m["constraints"].append(copy.deepcopy(m["constraints"][0])),
            lambda m: m["decisions"][0]["options"].append(copy.deepcopy(m["decisions"][0]["options"][0])),
            lambda m: m["project"].update(hidden_discount=0.5),
            lambda m: m["decisions"].clear(),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(case=index):
                model = example()
                mutate(model)
                with self.assertRaises(optimize.ModelError):
                    optimize.solve(model)

    def test_invalid_limit_is_rejected(self):
        for values in [{"max_states": True}, {"time_limit": float("nan")}, {"top_k": 0}, {"backend": "invented"}]:
            with self.subTest(values=values), self.assertRaises(optimize.ModelError):
                optimize.solve(example(), **values)

    def test_duplicate_json_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "duplicate.json"
            path.write_text('{"schema_version":"1.0","schema_version":"2.0"}')
            with self.assertRaises(optimize.ModelError):
                optimize.load_json(path)

    def test_nan_json_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "nan.json"
            path.write_text('{"value":NaN}')
            with self.assertRaises(optimize.ModelError):
                optimize.load_json(path)

    def test_output_is_not_silently_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "result.json"
            optimize.write_output(path, "original")
            with self.assertRaises(FileExistsError):
                optimize.write_output(path, "replacement")
            self.assertEqual(path.read_text(), "original")

    def test_cli_invalid_input_writes_model_invalid(self):
        with tempfile.TemporaryDirectory() as temp:
            model = Path(temp) / "model.json"
            output = Path(temp) / "run.json"
            model.write_text('{"schema_version":"wrong"}')
            with redirect_stdout(io.StringIO()):
                code = optimize.main([str(model), "--output", str(output)])
            self.assertEqual(code, 2)
            self.assertEqual(json.loads(output.read_text())["status"], "MODEL_INVALID")

    def test_report_recalculates_result(self):
        result = optimize.solve(example())
        result["best_solution"]["total_cost"] -= 1
        with self.assertRaises(optimize.ModelError):
            render_report.render(result)

    def test_report_checks_snapshot_hash(self):
        result = optimize.solve(example())
        result["model_snapshot"]["project"]["name"] = "Changed"
        with self.assertRaises(optimize.ModelError):
            render_report.render(result)

    def test_report_does_not_conflate_unknown_and_infeasible(self):
        report = render_report.render(optimize.solve(example(), max_states=1))
        self.assertIn("**Status:** UNKNOWN", report)
        self.assertIn("No conclusion about feasibility", report)
        self.assertIn("Calculation appendix only", report)

    def test_report_escapes_untrusted_labels(self):
        model = example()
        model["project"]["name"] = "<script>alert(1)</script>\n# Fake title"
        report = render_report.render(optimize.solve(model))
        self.assertNotIn("<script>", report)
        self.assertIn("&lt;script&gt;", report)

    def test_near_limit_model_run_can_still_be_rendered(self):
        # A valid model near 5 MiB grows beyond 5 MiB after the run adds its
        # snapshot formatting and metadata. The run loader needs its own cap.
        model = example()
        count = 2000
        model["evidence"].extend({"id": f"Fixture{i}", "source": "x", "locator": "Synthetic size-boundary fixture"}
                                  for i in range(count))
        baseline_size = len(json.dumps(model, separators=(",", ":")).encode())
        source_length = 1 + (optimize.MAX_INPUT_BYTES - 12000 - baseline_size) // count
        self.assertLess(source_length, 4000)
        for item in model["evidence"][1:]:
            item["source"] = "x" * source_length
        model_bytes = json.dumps(model, separators=(",", ":")).encode()
        self.assertLess(len(model_bytes), optimize.MAX_INPUT_BYTES)
        with tempfile.TemporaryDirectory() as temp:
            model_path = Path(temp) / "model.json"
            model_path.write_bytes(model_bytes)
            result = optimize.solve(optimize.load_json(model_path))
            run_text = json.dumps(result, indent=2)
            self.assertGreater(len(run_text.encode()), optimize.MAX_INPUT_BYTES)
            run_path = Path(temp) / "run.json"
            run_path.write_text(run_text)
            report_path = Path(temp) / "report.md"
            with redirect_stdout(io.StringIO()):
                code = render_report.main([str(run_path), "--output", str(report_path)])
            self.assertEqual(code, 0)
            self.assertTrue(report_path.is_file())

    @unittest.skipUnless(importlib.util.find_spec("ortools"), "Optional OR-Tools package not installed")
    def test_cp_sat_matches_enumeration(self):
        for model in [example(), resource_model()]:
            expected = optimize.solve(model)
            actual = optimize.solve(model, backend="cp-sat", time_limit=10)
            self.assertEqual(actual["status"], expected["status"])
            self.assertEqual(actual["objective"]["best_value"], expected["objective"]["best_value"])
            self.assertTrue(actual["best_solution"]["validation"]["passed"])
            render_report.render(actual)

    @unittest.skipUnless(importlib.util.find_spec("ortools"), "Optional OR-Tools package not installed")
    def test_cp_sat_infeasible_and_zero_budget(self):
        model = example()
        model["budget_total"] = 0
        self.assertEqual(optimize.solve(model, backend="cp-sat")["status"], "INFEASIBLE")
        self.assertEqual(optimize.solve(model, backend="cp-sat", time_limit=0)["status"], "UNKNOWN")

    @unittest.skipUnless(importlib.util.find_spec("jsonschema"), "Optional schema validation package not installed")
    def test_json_schema_matches_supported_examples_and_rejects_boolean_money(self):
        import jsonschema
        schema = json.loads((ROOT / "assets" / "model.schema.json").read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
        validator = jsonschema.Draft202012Validator(schema)
        validator.validate(example())
        validator.validate(resource_model())
        model = example()
        model["decisions"][0]["options"][0]["monthly_cost"] = True
        with self.assertRaises(jsonschema.ValidationError):
            validator.validate(model)


if __name__ == "__main__":
    unittest.main()
