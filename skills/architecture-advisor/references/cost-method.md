# Cost, resources and attribution

## Model a comparable decision

Declare currency and integer scale, analysis period, horizon, cost completeness, cost basis (incremental or total), and baseline. Separate build/migration from recurring license, usage, compute, storage, network, support and operations costs. Use actual contract and billing evidence or mark estimates explicitly. Record price dates and renewal assumptions.

Keep shared fixed resources as one modeled choice with dependencies and combined capacity; do not duplicate their fixed cost for every consumer. Do not subtract a baseline with a different service level and call the difference a saving. Distinguish reduced invoices, avoided future purchases, released prepaid capacity, and internal attribution. Include migration and ongoing operating cost when comparing changes.

The bundled optimizer uses a fixed monthly amount across the stated horizon and integer additive metrics. It does not forecast changing prices, amortization, taxes, tiered usage, discounting, correlated outages or queuing behavior. Encode approved whole-pattern estimates or use an appropriate richer model for those cases and disclose the method.

## Exact shared-cost allocation

Run scripts/allocate_costs.py with a JSON object like examples/allocation.json. Required fields are schema_version 1.0, currency, currency_scale, period, and applications. Applications have unique id, optional label and nonnegative integer direct_cost. Each shared_pools entry has unique id, nonnegative integer cost, a nonempty allocation_basis and weights keyed by application ID.

Costs are integer currency units divided by currency_scale. A scale of 1 means whole units; 100 means hundredths. Supported scales are 1, 10, 100, 1000 and 10000. Decimal weights may be strings; they are relative weights and need not sum to one. Missing application weights mean zero. Negative weights, unknown applications, duplicate IDs and duplicate JSON keys are rejected. The script does not establish whether a policy is economically fair.

For each pool, normalize nonnegative weights, allocate floor amounts, then distribute remaining integer units by largest fractional remainder. Ties use application ID order. This exactly reconciles the supplied source amount without binary floating-point currency error. If all weights are zero, keep the entire pool explicitly unallocated. Direct costs must exclude the shared pools to avoid double-counting.

Outputs include per-application attribution, pool breakdown, unallocated amounts and reconciliation totals. The tool does not modify bills or allocate real money. It does not support negative credits or exchange-rate conversion; normalize these with a documented accounting policy before use.

## Evidence and reporting

Show actual cost, allocated cost and potential avoidable cost as separate measures. Cite the price/usage source and the agreed allocation policy. Use sensitivity scenarios for estimated demand or cost; do not present more precision than the inputs justify. An unknown price is not free, and an omitted metric is not an unknown quantity that may safely be treated as zero.
