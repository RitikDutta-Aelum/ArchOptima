# Architect-facing report contract

## Choose the response depth

For a narrow question, use: Recommendation; Rationale and evidence; Trade-offs; Next action. Avoid forcing a full review onto a one-line question.

For a substantive review, use the headings in assets/architecture-report.md. Lead with a decision, not a summary of the uploads. Write enough detail for an architect to assess the recommendation without reading every source. Preserve meaningful uncertainties next to the affected decision.

## Decision status

Use Recommended when the evidence and modeled requirements support selection. Use Conditional recommendation when a named assumption or pending verification could change the decision. Use Decision deferred when a material gap prevents choosing among options. Use No feasible option under the supplied constraints only with a completed solver proof or an explicit, complete comparison of the finite catalog. Keep mathematical solver status separate from business decision status.

## Required substance for a full report

1. Executive decision: decision status, selected direction, 2-4 decision drivers, main condition, scope and horizon.
2. Scope and evidence: source inventory, version/hash if available, locations inspected, visual/extraction coverage, exclusions, material assumptions and conflicts.
3. Architecture assessment: current-state components and flows; proposed changes; relevant trust and failure boundaries; labeled diagram when useful.
4. Requirements and constraints: ID, requirement, hard/preference, source, evaluation and gap. Explain derived performance/capacity assumptions.
5. Options and trade-offs: comparable candidates, hard-constraint eligibility, cost/capacity/delivery/operations implications, rejection reasons, baseline.
6. Cost and resource analysis: only if relevant; currency, integer scale, time horizon, one-time versus recurring, shared costs, contracts, sensitivity, and mathematical result status. Otherwise explicitly scope this out in a sentence, without a placeholder cost table.
7. Risks and verification: material failure mode, evidence, consequence, proposed mitigation, verification, owner role. Prioritize based on stated criteria; do not manufacture numeric risk scores.
8. Recommended actions: ordered actions with owner role and acceptance evidence, separating analysis/prototype from any future live change.
9. Decision record: decision, context, considered options, rationale, consequences, conditions, revisit trigger. It may be concise or a separate requested artifact.
10. Sources and limitations: readable source locators, current official URLs where browsed, unknowns and unsupported conclusions.

## Evidence and confidence

Use source records such as E-abc123-0001 and locators such as system.pdf p. 4; integration.pptx slide 3; costs.xlsx sheet Budget cell D12; overview.png upper-right legend. Cite material findings near their claims. A checksum establishes identity, not trustworthiness.

Separate five classes: observed from a file/visual; explicitly provided by the user; derived by shown calculation; assumed for analysis; unresolved. Use qualitative confidence with a reason when helpful. Do not invent probability percentages. Do not cite a source that was only mentioned by another document as though it was read.

A full report must explain source coverage. Extracted text does not imply that every diagram, annotation, formula, hidden sheet or image was inspected. Repeat unresolved source conflicts in the decision conditions when they change eligibility or ranking.

## Professional style

Use direct sentences and consistent component names. Define acronyms on first use. State the benefit and consequence of a choice together. Make tables comparable and use the same units and time basis. Avoid generic technology shopping lists, ungrounded architecture scores, promotional wording and fabricated guarantees.

Do not leave template tokens, empty headings, invented owner names, or unsupported timelines. Use an owner role when the person is unknown. Cite a real file or verified URL, not a placeholder. Label all demonstrations Synthetic example. Never describe a mathematical bound, a solver objective value, or a paper claim as realized customer savings.

## Final checks

Check that the selected design survives the stated hard constraints; cost arithmetic reconciles; baseline and candidate have comparable service requirements; trade-offs explain rejected alternatives; unknowns have a proposed verification step; and the next action is specific. The bundled report checker verifies structure only. Human/agent review is still required for correctness and usefulness.
