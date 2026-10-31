# Architecture evaluation method

## Build the model of the decision

Identify actors, required capabilities, data stores, systems of record, external dependencies, execution environments, and deployment/trust boundaries. Keep current state separate from proposed state. Reuse original component names until ambiguities are resolved.

Turn prose into testable requirements. Replace vague phrases such as scalable or highly available with named workloads, service targets, recovery scenarios, or a clearly marked unknown. Do not silently promote a guess into a mandatory constraint.

## Evaluate only relevant dimensions

| Dimension | Questions that can change the decision |
| --- | --- |
| Functional fit | Which capability does each component provide? What behavior is preserved or changed? |
| Data | Who owns each record? How are consistency, retention, deletion and residency handled? |
| Integration | What happens on timeout, retry, duplicate delivery, reordering or partial success? Are idempotency and limits specified? |
| Security | Which identity crosses which trust boundary? What access is necessary? What evidence supports isolation and encryption claims? |
| Performance | Which observed or tested workload is supported? What is the bottleneck? What changes at peak and during recovery? |
| Reliability | Which component failures are covered? Are shared dependencies a common failure point? What recovery evidence exists? |
| Operations | Who monitors, diagnoses, restores, upgrades and owns the service? What support load does customization introduce? |
| Delivery | What dependencies, skills, migration steps and rollback decisions affect feasibility? |
| Cost | What is fixed, variable, committed, incremental, shared, uncertain or avoidable? |

Do not sum independent service capacities when the request traverses them in series. Do not multiply availability figures without justified independence assumptions. Do not infer a recovery objective from the existence of backups. Prefer measured operating envelopes and explicit failure tests.

## Compare fairly

Use the same functional requirements, horizon, demand scenario and included cost categories for each candidate. Include the baseline when known. Explain which hard requirement eliminates an option. Keep important dimensions visible; use weights only if the user or decision owner has supplied and accepted them.

For robustness, vary a small number of decision-driving assumptions: peak demand, growth, paid usage, delivery effort, commitment end date, isolation, or failure scenario. Show the threshold at which the recommendation changes when calculable. Avoid false precision when source uncertainty is wider than the reported cost difference.

## Explain infeasibility and partial results

When a completed search proves no eligible combination, report the model scope and identify the conflicting requirements using actual checks. An infeasibility certificate does not show that all conceivable architectures are impossible. If the engine does not provide an unsatisfiable core, do not invent one; test proposed relaxations explicitly or describe likely conflicts as hypotheses.

When time limits stop the run, report the feasible incumbent and bound if available, or state that no answer was established. A mathematical optimum cannot establish the completeness of the catalog or the truth of real-world inputs.

## Review authorization

Architecture analysis can recommend future changes. Do not deploy them, alter production settings, buy services, send stakeholder communications, or use customer credentials as part of a review without corresponding authorization. This is a scope boundary, not a reason to delay a useful recommendation.
