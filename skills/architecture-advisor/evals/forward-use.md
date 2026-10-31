# Synthetic forward-use evaluation

**Case:** Workflow processor architecture with missing commercial and acceptance evidence

**Recorded run:** 31 October 2026

**Result:** PASS for this case; production selection correctly deferred

This is an entirely synthetic evaluation. The fixtures contain no private user paper or customer data. The result demonstrates behavior on one bounded scenario, not general architecture-review accuracy or a production deployment.

## Scenario and inputs

The request asks for the cheapest suitable production architecture from two supplied candidates. The hard requirements include 100 jobs/minute after losing a worker, India-only customer data and backups, a recurring project budget of INR 100,000/month, preservation of the hosted ServiceNow boundary, and demonstrated tenant isolation if workers are shared.

Candidate A is the current single-worker arrangement: INR 130,000/month and zero capacity after worker loss. Candidate B proposes shared redundant workers, but its monthly price is blank and its capacity is an untested vendor estimate. The diagram is current state, not an approved target.

| Fixture | Relevant evidence |
| --- | --- |
| [requirements.md](../examples/review-case/requirements.md) | Revision 2, lines 3–7 contain R1–R5; lines 8–10 identify current state, unknown B pricing and untested capacity. |
| [candidates.csv](../examples/review-case/candidates.csv) | Row 1 defines units; row 2 contains A; row 3 contains B and the blank monthly price. |
| [current-architecture.png](../examples/review-case/current-architecture.png) | Entire image; center worker box, right database/backup box, directional arrows and footer. |

## Reproduce

Use a host with text-file access and image inspection. Read the skill's `SKILL.md` and applicable references. For an independent run, do not read the example answer until the new review is complete. Give the reviewer this task from the skill root:

> Use architecture-advisor to review `examples/review-case/requirements.md`, `examples/review-case/candidates.csv`, and `examples/review-case/current-architecture.png`. Recommend the cheapest suitable production design and produce a professional structured report with evidence and explicit conditions. These are synthetic case files. Do not modify the skill or any production system.

Save the new report to a separate output location, then assess it against the criteria below. No optimizer is needed to compare these two rows; an optimizer cannot supply a missing price or prove an untested capacity claim. Public authoritative documentation may be used to verify region-code geography without sending the case files elsewhere.

The recorded example answer is [architecture-review.md](../examples/architecture-review.md). Its source links resolve to the packaged fixtures. To reproduce its structural check from the skill root:

```bash
python3 scripts/check_report.py examples/architecture-review.md
```

The checker tests report structure only. Human or agent review must assess evidence, arithmetic and recommendation quality.

## Pass/fail criteria and observed result

Every criterion below is required to pass this case.

| Criterion | Pass condition | Recorded result |
| --- | --- | --- |
| Decision calibration | Defer production selection; conditionally advance B for verification. Do not claim B is cheapest, optimal or production-ready. | PASS — executive decision and decision record use that status. |
| Hard constraints | Reject A because 0 < 100 jobs/minute and INR 130,000/month > INR 100,000/month. Lower one-time cost cannot offset failure. | PASS — explicit R1/R3 exclusion. |
| Missing price | Preserve B's recurring price as unknown; never substitute zero or calculate numerical savings from it. | PASS — complete-cost condition is quote plus excluded recurring costs ≤ INR 100,000/month. |
| Capacity evidence | Keep 130 jobs/minute labeled as a vendor estimate; require a real failed-worker test. | PASS — estimated 30 jobs/minute margin is distinguished from measured capacity. |
| Residency | Do not treat worker-region labels as proof of all customer-data and backup locations. Include the hosted platform and external database in the open evidence. | PASS — full-path residency remains an acceptance gate; current backup location is identified as unknown. |
| Hosted boundary and isolation | Preserve R4; require demonstrated tenant isolation before accepting shared workers under R5. | PASS — no ServiceNow operating-system or database-engine selection is proposed. |
| Visual provenance | Inspect the original image; identify it as current state, preserve shown arrow directions and unknown protocols/backup location. | PASS — full image inspected and observations localized. |
| Financial distinctions | Separate one-time and recurring costs; do not call the INR 250,000 catalog difference switching cost or imply historical A spend is a new outlay. | PASS — these limitations are explicit. |
| Mathematical claims | Do not claim global infeasibility or an optimization proof. Incomplete evidence is not proof that B fails. | PASS — direct comparison only; no optimizer run or optimum claimed. |
| Actionability and provenance | Provide R1–R5 traceability, owner roles, concrete acceptance evidence and readable source locators. | PASS — full report contains all of these. |
| Portability and structure | Keep synthetic labels prominent, use resolvable relative fixture links, omit internal workspace paths and unavailable extraction artifacts, and pass the structural checker. | PASS — checker returned no errors or warnings; seven relative fixture links resolve. |

## Recorded verification and limits

The reviewer read both text files and visually inspected the complete image. An independent reviewer checked the cost and eligibility conclusions and the portable package. That review prompted a wording correction: the decline from 130 to 100 jobs/minute is 23.1% of the estimate, while 130 is 30% above the 100 requirement. The report now states the denominator explicitly. The packaged fixtures were verified byte-identical to the synthetic inputs; their SHA-256 values appear in the report. The official AWS region table supports only the geographical interpretation of `ap-south-1` and `eu-west-1`, not an assertion about actual deployment or residency.

`check_report.py` returned `passed: true`, with empty `errors` and `warnings`. Additional portability checks confirmed the relative links, fixture hashes and absence of internal workspace paths or references to an unavailable extraction bundle. These checks establish packaging integrity and structure; they do not make the vendor estimate measured, complete the quote or certify a real architecture.
