# Finite architecture optimization model

## Contents

1. Scope and guarantees
2. Input contract
3. Modeling resources and scenarios
4. Commands and outputs
5. Status and evidence interpretation
6. Limits and extension points

## 1. Scope and guarantees

Use this script when a reviewed finite catalog, additive costs and metrics, and
explicit hard constraints adequately represent the user's decision. Do not force
a vague architecture question into numerical optimization. First identify missing
requirements and produce a qualitative assessment when necessary.

The bundled solver minimizes:

`sum(selected one_time_cost) + horizon_months * sum(selected monthly_cost)`.

Select exactly one option from each decision. Enforce aggregate metric bounds,
option dependencies, incompatibilities, and an optional whole-horizon budget.
The standard-library backend enumerates combinations with state/time limits. An
optional OR-Tools CP-SAT backend compiles the same model into Boolean variables
and integer linear expressions. Neither backend implements the ETH research
paper, proves the architectural model correct, or establishes measured savings.

## 2. Input contract

Use `assets/model.schema.json` as the structural contract and
`scripts/optimize.py` for cross-reference and semantic validation. See
`examples/model.json` for a complete synthetic example.

| Field | Meaning |
| --- | --- |
| `schema_version` | Literal `"1.0"` |
| `project.name` | Human-readable project name |
| `project.currency` | Three-letter uppercase currency code |
| `project.currency_scale` | Power of ten: 1 for whole units, 100 for cents/paise, up to 1000000000 |
| `project.horizon_months` | Integer from 1 to 1200 |
| `project.cost_basis` | `incremental` or `total`; compare only consistent scopes |
| `project.cost_completeness` | `complete` or `partial`, as declared by the model author |
| `project.assumptions` | Optional array of explicit assumption strings |
| `metric_definitions` | Metric ID to `{unit, description}` mapping |
| `decisions` | Nonempty array; each decision has an ID, label, and options |
| `constraints` | Aggregate metric comparisons |
| `budget_total` | Optional nonnegative integer cost limit over the whole horizon |
| `evidence` | Optional source register with unique `id`, `source`, `locator`, and optional `note` |

An option requires `id`, `label`, `one_time_cost`, `monthly_cost`, and `metrics`.
Costs must be nonnegative integers in the project's stated scale. Convert decimal
source prices using exact decimal arithmetic and document rounding before creating
the model. Booleans, floats, NaN, and infinity are rejected as numeric values.
Prices in different currencies must be converted with a dated, cited rate first.

An option may include `requires`, `incompatible_with`, and `evidence_ids` arrays.
Reference options with `decision_id.option_id`. IDs start with a letter and contain
only letters, digits, underscores, and hyphens. References must resolve to declared
objects. Repeated IDs and unsupported fields are rejected.

A metric is the integer sum of the selected options' contributions. **A missing
metric contribution means zero**, not an estimate or unknown value. Do not omit a
contribution when its value is actually unknown. Mark the input gap and stop that
quantitative analysis or use clearly separated, user-approved scenarios.

A constraint has `id`, `metric`, `op`, `value`, and `description`, with optional
`evidence_ids`. Operators are `>=`, `<=`, and `==`. Use two bounds for an interval.
The script does not interpret arbitrary text constraints or Boolean expressions.
The constraint ID `budget_total` is reserved for the optional budget check.

Evidence IDs retain provenance; the script neither opens nor authenticates cited
sources. Empty references are allowed and generate a qualification. Inventing an
evidence record does not verify a claim. Keep observations, estimates, and assumptions
separate in the full architecture report.

## 3. Modeling resources and scenarios

**Count a shared fixed cost once.** Represent a shared resource as its own decision
with `off` and `on` options. Put its fixed cost in the `on` option. A consumer's
option can require `shared_pool.on`. Do not repeat that pool cost in every consumer.

For each pool, a capacity-balance metric can give the resource a positive capacity
and each assigned consumer a negative demand. Require the sum to be at least zero.
Use distinct metrics for distinct pools and dimensions such as memory, throughput,
and headroom. Do not mix units or add non-additive quantities like p95 latency.

For isolation, use incompatibility rules or separate approved configurations. For
all-or-nothing prerequisites, use `requires` links. Same-decision incompatible
choices are already mutually exclusive because exactly one option is selected.

Model failure and growth scenarios as separate reviewed runs, or as separate
scenario-specific balance metrics if the additive representation is valid. A
global metric such as "number of redundant components >= 1" does not prove that
every component meets its failover requirement. Use complete qualified candidates
or component-specific constraints. Throughput and failover inputs need engineering
evidence; the optimizer does not simulate the running system.

Keep actual invoiced cost, allocated/showback cost, avoidable future cost, and
prepaid commitments distinct. The model has one declared cost basis and does not
infer contract terms, licensing allowances, utilization savings, or cost attribution.

## 4. Commands and outputs

Run from the installed skill directory (or use absolute script/file paths):

```bash
python scripts/optimize.py examples/model.json --output work/run.json --backend enumerate --time-limit 30 --max-states 100000 --top-k 3
python scripts/render_report.py work/run.json --output work/calculation.md
```

Existing output files are refused. Create a new run directory when rerunning.
`top-k` is from 1 to 20 and includes the best candidate. Enumeration retains the
cheapest candidates among assignments actually examined. Equal-cost ties are
ordered by option IDs. CP-SAT may choose a different equal-cost optimum and obtains
additional candidates by excluding earlier choices within the same time budget.
These alternatives are not guaranteed to be structurally diverse or a Pareto set.

The JSON output includes the full model snapshot and its canonical SHA-256, backend,
status, limits, elapsed search time, theoretical combinations, available search
statistics, best objective and bound, returned selections, recalculated constraint
checks, alternatives, and qualifications. A result is local and contains no external
service calls. Counts of examined/retained candidates are **not** a #SAT result.

Use the Markdown renderer for a deterministic calculation appendix. It checks the
model hash and recalculates each selection. It does not re-prove a claimed optimum
or infeasibility, assess evidence quality, or produce the complete architect-facing
report. Apply the main skill's reporting instructions for that report.

## 5. Status and evidence interpretation

| Status | Meaning |
| --- | --- |
| `OPTIMAL` | Exhaustive enumeration completed, or CP-SAT proved the encoded objective optimum |
| `FEASIBLE` | A validated modeled solution exists; search stopped without proving optimality |
| `INFEASIBLE` | A complete search or solver proof established no feasible listed combination |
| `UNKNOWN` | No solution/proof was established before the limit; do not claim infeasibility |
| `MODEL_INVALID` | The input contract was violated; no solve conclusion follows |
| `ERROR` | File access, optional dependency, or backend failure; no solve conclusion follows |

Exit code 0 means a mathematical run completed, including `UNKNOWN` and
`INFEASIBLE`; it does not mean a feasible design exists. Invalid inputs return 2.
Environment/backend/output failures return 3. Read the JSON status.

For partial costs, `OPTIMAL` means minimum of the **partial encoded objective**.
Do not describe it as lowest TCO. For complete costs, state that completeness was
declared by the author, and that the optimum remains conditional on the catalog,
constraints, estimates, and scenarios. A verified source reference is not an
optimality proof, and an optimality proof does not verify source estimates.

## 6. Limits and extension points

The script accepts at most 5 MiB of model JSON, 200 decisions, 10000 total options,
1000 metric definitions, and 10000 constraints. Integers are bounded to +/-10^18
at input; option costs must be nonnegative. Enumeration handles exact integer
arithmetic but grows exponentially. The time limit is cooperative between complete
assignments, so one evaluation and model validation can exceed the requested budget.
Use the harness's process timeout/resource limits when a hard runtime cap is needed.
The report renderer separately accepts run JSON up to 32 MiB because the retained
model snapshot, formatting, candidates, and checks can exceed the input model's size.
Reduce model/evidence verbosity or retained candidates if a run exceeds that limit.

CP-SAT is tested with `ortools==9.15.6755`; install it using
`requirements-optimization.txt` in a virtual environment. Its backend additionally bounds expression
magnitudes to 2^52-1 for safely reported whole-unit objective bounds. Rescale a
model deliberately or use enumeration if that restriction matters. `max_states`
does not apply to CP-SAT. No package is downloaded or installed by these scripts.

For continuous allocation, nonlinear performance, time-varying scheduling,
probabilistic reliability, uncertainty optimization, or detailed license logic,
select a suitable model/solver and document the change. Do not claim the bundled
additive model implements those features. Preserve the reviewed input contract,
source locators, independent result checking, and honest solver status.

Primary solver reference: https://developers.google.com/optimization/cp/cp_solver
