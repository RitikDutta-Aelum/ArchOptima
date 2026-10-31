# Run the illustrative model

Run these commands from the skill directory. Use a new output directory for each run.

```bash
python scripts/optimize.py examples/model.json --output work/example/run.json
python scripts/render_report.py work/example/run.json --output work/example/calculation.md
```

On systems where Python is named `python3`, substitute `python3`. On Windows,
`py -3` may be used. The default enumeration backend has no package dependencies.

Expected result: `OPTIMAL`, selecting `processing.shared_redundant` with a modeled
24-month incremental cost of `3130000` integer INR units. The dedicated option
costs `3770000`. The single-worker option fails both constraints. All numbers are
synthetic; the result is not an estimate for any real ServiceNow deployment.

To explore demand growth, copy the JSON to a new file and change the value of
`R-capacity` to `150`. The dedicated redundant option should become the minimum
modeled feasible choice. At `201`, no listed design is feasible.

To demonstrate an interrupted search without implying infeasibility:

```bash
python scripts/optimize.py examples/model.json --max-states 1 --output work/limited/run.json
```

Expected status: `UNKNOWN`. Only the first, infeasible option was evaluated.
With `--max-states 2`, the status is `FEASIBLE`; the shared design has been found,
but the search was deliberately stopped before examining every combination.

## Optional CP-SAT backend

Create a virtual environment before installing optional packages. The following
installs the release tested with this package:

```bash
python -m pip install -r requirements-optimization.txt
python scripts/optimize.py examples/model.json --backend cp-sat --time-limit 30 --output work/cpsat/run.json
```

CP-SAT respects the time limit; `--max-states` applies only to enumeration. The
program records an independent recalculation of every returned selection. Its
run report is a calculation appendix, not a replacement for the architect-facing
assessment described in `SKILL.md`.

Do not upload private architecture files, customer contracts, cost exports,
generated `work/` directories, or credentials with this public example.
