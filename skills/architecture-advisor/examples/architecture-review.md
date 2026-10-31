# Synthetic workflow processing — Architecture Decision Review

**Synthetic evaluation case**

**Decision status:** Decision deferred for production selection; conditionally advance Candidate B for validation and final pricing.

**Scope and horizon:** Hosted ServiceNow workflow integration, external processing, customer-data locations and backups. Recurring affordability is assessed per month; one-time costs are separate. No investment horizon was supplied.

**Prepared for:** Solution architect and project decision owner

**Evidence reviewed:** 31 October 2026; requirements revision 2

## 1. Executive decision

**The cheapest suitable production design cannot yet be established. Reject Candidate A as a compliant target and take Candidate B through a defined evidence and commercial gate.** Candidate B is the only supplied candidate with a plausible route to meeting the requirements, but it is not yet proven suitable or affordable. Its missing monthly price must remain unknown. [R, lines 3–10; C-A; C-B]

The decision rests on four findings:

1. **Candidate A fails two hard requirements outright.** Its capacity after loss of its only worker is 0 jobs/minute against a required 100. Its INR 130,000/month recurring figure exceeds the INR 100,000/month cap by INR 30,000/month. A lower listed one-time cost cannot compensate for either failure. [R, lines 3 and 5; C-A]
2. **Candidate B has an encouraging estimate, not a verified capacity result.** The catalog states 130 jobs/minute after one worker fails, but the requirements explicitly say this is an untested vendor estimate. The 30 jobs/minute margin above the requirement is therefore estimated headroom. [R, line 10; C-B]
3. **Residency must cover the complete customer-data path.** Candidate B's `ap-south-1` region identifies Mumbai, India, while Candidate A's `eu-west-1` identifies Ireland. However, a worker-region label does not establish the locations of the hosted ServiceNow data, external database, backups or other customer-data copies. The current image explicitly leaves the backup location unknown. [C-A; C-B; V1, center and right boxes; W1]
4. **Shared workers are a conditional permission.** Candidate B requires demonstrated tenant isolation and a final, complete recurring project cost of no more than INR 100,000/month. Neither is established by the supplied proposal row. [R, lines 5, 7 and 9; C-B]

**Recommended production direction, subject to these conditions:** retain the hosted ServiceNow boundary and validate an India-resident external worker pool with sufficient surviving capacity after any one worker is lost. Keep every customer-data store and backup in India, and prove isolation for the shared pool. Select B only when those conditions and the budget are satisfied. If any condition fails, request a revised design or additional candidates; the current catalog does not support naming another production winner.

## 2. Scope and evidence

The review used the supplied files as synthetic evidence. The cited invoice and vendor proposal were described in the CSV; the underlying invoice, proposal and contract were not supplied or independently audited.

| Reference | Source and locator | Coverage and evidential status |
| --- | --- | --- |
| R | [requirements.md](review-case/requirements.md), revision 2, lines 1–10 | All lines read in full. User-provided requirements and explicit limits on price/capacity evidence. |
| C-A | [candidates.csv](review-case/candidates.csv), header row 1 and Candidate A row 2 | All fields read. The CSV reports an existing invoice and topology as its basis; those originals were not supplied. |
| C-B | [candidates.csv](review-case/candidates.csv), header row 1 and Candidate B row 3 | All fields read. Blank monthly cost preserved as unknown; capacity treated as a vendor estimate. |
| V1 | [current-architecture.png](review-case/current-architecture.png), frame 1, entire 1200 × 540 image | The original image was visually inspected: all three boxes, both arrowheads, title and footer were readable. These are direct visual observations; image metadata alone does not establish them. |
| W1 | [AWS Regions, Available AWS Regions table](https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-regions.html), accessed 31 October 2026 | Official reference used solely to verify the geographical meaning of the two region codes. It is not evidence of the actual deployments or their data residency. |

All three packaged fixtures were reviewed in full, with no unreadable text or image regions identified. The image was visually inspected separately from reading the text files; no optical character recognition was needed. The source hashes in section 10 identify the exact packaged fixtures and were verified after packaging.

Material evidence classes and assumptions are kept distinct:

- **Observed:** the diagram shows one external worker in `eu-west-1`, an external database, an unknown backup location and arrows directed from the hosted application to the worker and then to the database. [V1]
- **User-provided:** R1–R5, both candidate cost entries, the missing B price and the untested nature of B's capacity. [R; C-A; C-B]
- **Derived:** the budget and capacity margins in section 6, calculated from those supplied figures.
- **Assumed for review:** “recurring project budget” means all recurring costs attributable to this project, counted once. The exact commercial scope still needs agreement. Because R2 says customer data and backups, the residency inventory must include any customer-data copies in logs, queues, exports or recovery paths as applicable; this does not assert that such components currently exist.
- **Unresolved:** whether the current worker handles customer data, the locations and resilience of the hosted platform and external database, complete prices, contract commitments, proposed worker count, tenant-isolation controls and representative workload characteristics.

There is no source conflict: a deployed arrangement can fail later review criteria. The current-state image is expressly not an approved proposal. [R, line 8]

## 3. Architecture assessment

### Current deployed arrangement

The diagram contains a hosted ServiceNow workflow application, one external AWS worker in `eu-west-1`, and an external database. The first arrow points from ServiceNow to the worker; the second points from the worker to the database. It does not establish response paths, synchronous or asynchronous operation, protocols, authentication, encryption, database location or database redundancy. The footer expressly says no worker redundancy is shown and protocols are unspecified. [V1, left, center and right boxes, arrows and footer]

The external worker is a demonstrated single point of failure for the required processing capacity: Candidate A explicitly has zero surviving capacity after losing one worker. This is a finding about the stated worker-loss scenario, not an availability calculation for the complete application. [C-A; R, line 3]

The hosted platform, external processing and database represent separate ownership and access boundaries that the detailed design must document. If customer data passes through the shown Ireland worker, that path is incompatible with R2. Even if that worker processes only non-customer information, the current materials still do not establish India residency for the customer-data stores and backups. [R, line 4; V1; W1]

### Proposed direction for Candidate B

The CSV names “shared redundant external workers” in `ap-south-1`. It does not provide a complete target topology. The following are proposed acceptance conditions, not observations about an already implemented B design. [C-B]

- Keep ServiceNow as the hosted workflow platform. Do not select its operating system or database engine. Verify the platform's customer-data and backup locations through the relevant service evidence. [R, lines 4 and 6]
- Use the smallest worker-pool configuration that demonstrates the required surviving throughput under the agreed workload and tenant mix. Worker count, sizing and placement must come from that evidence; the estimate alone cannot determine them. [R, line 3; C-B]
- Establish India-only customer-data processing, storage, backup and restore locations throughout the applicable path. Document which data crosses each boundary and which party is responsible for it. [R, line 4]
- Demonstrate tenant separation in authorization, data access, secrets and processing state. Check resource contention during the failed-worker test so sharing does not undermine R1. [R, lines 3 and 7]
- Specify job retry, duplicate handling, failure detection and recovery behavior before production acceptance. These are proposed design checks because the current arrows provide no behavioral contract. Avoid assuming a queue, protocol or integration product is already present. [V1, footer]

Single-worker survival does not establish resilience to a database failure, shared dependency failure, availability-zone loss or regional loss. No recovery-time or recovery-point target was supplied. The architect should record these open decisions without silently turning them into additional mandatory requirements.

## 4. Requirements and constraints

| ID | Requirement and type | Source | Candidate A | Candidate B and required evidence |
| --- | --- | --- | --- | --- |
| R1 | Sustain at least 100 jobs/minute after losing one worker. **Hard constraint.** | R, line 3 | **Fail:** catalog states 0 jobs/minute after the failure. [C-A] | **Unverified:** estimate is 130. Require representative sustained processing with a worker unavailable, including the shared tenant mix and a recorded measurement basis. [C-B; R, line 10] |
| R2 | Customer data and backups remain in India. **Hard constraint.** | R, line 4 | **Not demonstrated; incompatible if customer data uses the shown Ireland worker.** Backup location is unknown. [V1; W1] | **Unverified end to end:** proposed worker region is India, but platform, database, backup and other applicable copy locations need evidence. [C-B; W1] |
| R3 | Recurring project cost no more than INR 100,000/month. **Hard constraint.** | R, line 5 | **Fail:** INR 130,000/month. [C-A] | **Unknown:** final recurring quote is outstanding. Require a complete project cost schedule within the cap. [R, line 9; C-B] |
| R4 | ServiceNow remains hosted; do not choose its operating system or database engine. **Hard scope constraint.** | R, line 6 | Hosted deployment is shown; no prohibited changes are proposed by this review. [V1] | The recommended direction preserves this boundary. Detailed supplier design must do the same. |
| R5 | Shared external workers are allowed only if tenant isolation is demonstrated. **Conditional hard requirement when sharing is used.** | R, line 7 | Sharing is not established by the supplied A description. No isolation conclusion is needed to reject A under R1/R3. | **Unverified:** sharing is explicit, but no isolation demonstration was supplied. Require design evidence and negative access tests. [C-B] |

For testing, “jobs/minute” should be operationalized as completed valid jobs, with workload, observation interval, tenant mix and failure timing recorded. That is a proposed measurement definition for the decision owner to agree, not an existing test result. Any allowable interruption during failure detection also needs an explicit decision; the supplied requirement does not define one.

## 5. Options and trade-offs

| Option | Hard-constraint eligibility | Benefits supported by evidence | Costs and operating consequences | Disposition |
| --- | --- | --- | --- | --- |
| A — current single worker | Ineligible under R1 and R3; R2 also lacks supporting evidence. | Existing arrangement, with a supplied recurring figure and an observed topology. | INR 600,000 listed one time; INR 130,000/month. Loss of its worker leaves zero stated capacity. [C-A] | Reject as a compliant target. Use only as the documented baseline for the review. |
| B — shared redundant external workers | Unresolved under R1, R2, R3 and R5. | Proposed redundancy; vendor-estimated surviving capacity above the requirement; India worker-region label; sharing allowed in principle. [R; C-B; W1] | INR 850,000 listed one time; recurring price unknown. Requires validated isolation, surviving capacity, residency and operating ownership. | Advance conditionally for evidence and pricing. Do not call it approved, cheapest or optimal. |

Only two catalog candidates were supplied, and neither is currently demonstrated to satisfy every hard constraint. This is **not proof that no feasible design exists**: B may qualify when evidence is completed. There are not two proven viable alternatives to compare, and none has been invented to fill that gap.

If B fails a gate, request revised India-resident shared or dedicated patterns with complete prices and the same failure test. Such patterns would be new options requiring evaluation, not approved alternatives from this catalog.

## 6. Cost and resource analysis

### Basis and inclusions

All amounts are in Indian rupees (INR), using whole rupees, scale 1. The supplied recurring costs and budget are monthly. One-time costs are reported separately without amortization. No contract term, tax basis, price date, growth forecast or investment horizon was supplied. The listed amounts do not establish a complete total cost of ownership. [R, line 5; C-A; C-B]

| Measure | Candidate A | Candidate B | Interpretation |
| --- | ---: | ---: | --- |
| Listed one-time cost, INR | 600,000 | 850,000 | Catalog figures. Confirm what remains payable; A's historical spend must not be treated as a fresh cost of continuing A. |
| Listed recurring cost, INR/month | 130,000 | Unknown | B's blank field is not zero. A's cited invoice was not supplied for scope reconciliation. |
| Complete recurring project cost, INR/month | At least the stated figure if additional project costs are excluded | Unknown | Required commercial basis for R3; ensure cost categories are included once. |
| Budget cap, INR/month | 100,000 | 100,000 | Fixed hard requirement. |
| Capacity after one worker fails, jobs/minute | 0 | 130, vendor estimate | Neither figure is an independently measured result in this review; B explicitly has no load test. |

The commercial gate should reconcile the worker service, any shared-pool allocation, database, storage, backups, network usage, monitoring, support, operations and any relevant hosted-platform or integration charges. These are categories to check for inclusion, not claims that every category creates an additional charge. Record commitments, usage limits, taxes, renewal assumptions and migration or parallel-running costs where applicable. If a shared-pool amount is allocated internally, distinguish that attribution from the actual invoice and incremental project spend.

### Transparent calculations and thresholds

**A's monthly excess:** INR 130,000 − INR 100,000 = **INR 30,000/month**, which is **30% above the cap**. Its post-failure capacity shortfall is 100 − 0 = **100 jobs/minute**. Both independently exclude A. [Derived from R, lines 3 and 5; C-A]

**B's estimated capacity margin:** 130 − 100 = **30 jobs/minute**, or **30% above the required rate**. A result below 100 in the required failure scenario fails R1 regardless of price. A result exactly at 100 meets the stated numerical threshold but demonstrates no margin above it; no extra headroom requirement has been invented. Achievable capacity could be roughly 23.1% below the 130 jobs/minute estimate before reaching the 100 jobs/minute requirement; no probability of that outcome can be inferred. [Derived from R, line 3; C-B; R, line 10]

Let **q** be B's final monthly quote and **o** be any other recurring project costs excluded from that quote, with each charge counted once. The budget condition is:

**q + o ≤ INR 100,000/month.**

Both quantities remain unresolved. A quote of INR 100,000/month leaves no allowance for additional excluded recurring charges. A quote below the cap can still fail R3 if the complete project cost exceeds it. A complete recurring total above the cap makes B ineligible under the current requirements; it does not authorize relaxing the budget.

The difference between B's INR 850,000 and A's INR 600,000 listed one-time amounts is INR 250,000, but that arithmetic is **not an established migration investment or switching cost**. No payback period is defensible without knowing sunk costs, termination commitments, remaining obligations, complete future costs and an agreed horizon. Likewise, the difference from A's spend is not demonstrated savings: B's recurring cost is unknown and A provides a lower service level. [C-A; C-B]

**Calculation status:** direct comparison of the supplied catalog only. No optimizer was run, and no mathematical optimum, total-cost minimum or production savings is claimed. Treating an unknown recurring price as zero would produce a misleading result. Additional solver machinery would not resolve missing commercial or engineering evidence.

## 7. Risks and verification

Priority below reflects whether the uncertainty blocks production selection, not a fabricated numeric score.

| Risk or uncertainty | Evidence and consequence | Proposed mitigation | Acceptance evidence | Owner role |
| --- | --- | --- | --- | --- |
| B is unaffordable after final scope is priced. **Selection blocker.** | Monthly price is unknown. R3 cannot be evaluated. [R, line 9; C-B] | Obtain a scoped final quote and reconcile all recurring project costs and allocation boundaries. | Signed commercial schedule or accountable cost approval demonstrating total recurring cost ≤ INR 100,000/month under the specified usage assumptions. | Procurement and finance/cost owner |
| B does not sustain throughput after a worker loss. **Selection blocker.** | 130 jobs/minute is untested. [R, line 10] | Run representative shared-workload tests with each relevant single-worker-loss scenario. Monitor valid completions, errors, queue growth if applicable and downstream limits. | Repeatable test evidence of ≥100 valid completed jobs/minute while one worker remains unavailable, with measurement interval and failure behavior agreed. | Performance engineer and external-service owner |
| Customer data or backups reside outside India. **Selection blocker.** | Current backup location unknown; B has only a worker-region label. [V1; C-B] | Build the full applicable data-location inventory; verify service configuration and supplier commitments, including restore destinations. | Reviewed evidence covering hosted ServiceNow, external processing, database, backups and other customer-data copies. | Data owner, platform owner and security architect |
| Shared tenants access each other's data or disrupt required capacity. **Selection blocker.** | R5 permits sharing only with demonstrated isolation. No demonstration supplied. [R, line 7] | Review tenant identity propagation and access controls; conduct negative access and contention tests. | Independent review and test results showing enforced tenant separation and R1 still met under the agreed tenant load. | Security engineer and external-service owner |
| Shared dependencies or job recovery introduce unexamined failures. **Design decision outstanding.** | Diagram omits protocols and redundancy beyond the single-worker observation. B topology absent. [V1; C-B] | Document dependencies, retry/duplicate behavior, restore procedure and ownership. Agree recovery targets appropriate to the business. | Target design, failure analysis, operating runbook and agreed recovery objectives; avoid claiming these already exist. | Solution architect and operations owner |

## 8. Recommended actions

| Priority | Action | Owner role | Acceptance evidence | Dependency |
| --- | --- | --- | --- | --- |
| 1 | Obtain B's complete final quote and confirm the project cost boundary. | Procurement and finance/cost owner | Itemized monthly total and commercial assumptions; no blank costs; one-time and recurring figures separated. | Needed before affordability or savings can be decided. |
| 1 | Confirm India residency across the complete customer-data path, including hosted ServiceNow and backups. | Platform owner, data owner and security architect | Data-flow/location register with configuration or supplier evidence for every applicable store and copy. | Needed for R2 acceptance; worker region alone is insufficient. |
| 1 | Agree the R1 workload and measurement protocol, then validate B under worker loss and shared tenant load. | Performance engineer and service owner | Reproducible failed-worker test showing ≥100 completed valid jobs/minute and documented failure-transition behavior. | Requires a representative non-production B configuration. |
| 1 | Demonstrate tenant isolation. | Security engineer and service owner | Access-control review, negative tenant tests and resource-contention evidence. | Must apply to the same B configuration tested for capacity. |
| 2 | Reconcile the evidence to R1–R5 and make the production selection. | Solution architect and project decision owner | A decision record showing every hard gate satisfied and the complete cost basis. | All selection blockers resolved. |
| 3 | After selection and separate implementation authorization, plan migration, rollback and acceptance. | Delivery and operations owners | Approved change plan, data handling plan and operating ownership. | Production approval and implementation authorization. |

These activities can establish a reviewable production decision. This review does not deploy a system, change ServiceNow settings, purchase services or authorize a live migration.

## 9. Decision record

**Decision:** Defer production selection and the claim of “cheapest suitable” design. Reject A as a compliant target. Advance B conditionally to final pricing and acceptance evidence.

**Context:** Requirements revision 2 mandates worker-loss throughput, India residency, a monthly recurring budget cap, preservation of the hosted ServiceNow boundary and demonstrated isolation for shared workers. The image is deployed current state, not an approved proposal. [R]

**Options considered:** A, the current single-worker arrangement, and B, proposed shared redundant external workers. No additional approved design was supplied. [C-A; C-B]

**Rationale:** A fails capacity and affordability. B addresses those design concerns in principle, but its capacity is estimated, its monthly price is unknown and residency/isolation evidence is incomplete. Selecting B now would confuse a plausible direction with an established suitable and costed design.

**Consequences:** Engineering and procurement effort should focus on the evidence that can qualify or disqualify B. The known noncompliance of the current baseline remains visible; it does not disappear while evaluation is pending. Any interim operating decision belongs to the project and service owners.

**Conditions for selection:** Demonstrated R1, complete India-only coverage for R2, recurring project total within R3, preservation of R4 and demonstrated R5. Even after B qualifies, describe it as the qualifying option from this supplied catalog; a broader claim of market-wide minimum cost would require a broader candidate search.

**Revisit triggers:** Final quote received; failed-worker test results available; isolation or residency finding; material workload change; revised requirements; or a newly supplied candidate. A cost above the cap or a failed hard requirement triggers redesign or additional options, not an unsupported exception.

## 10. Sources and limitations

### Source identity and locators

- **R:** [requirements.md](review-case/requirements.md), revision 2, lines 1–10. SHA-256: `8da366d6a7401ecef108c83d4f8a05455ff2695673f21794c26513fb16f829c6`.
- **C-A / C-B:** [candidates.csv](review-case/candidates.csv), row 1 headers, row 2 Candidate A, row 3 Candidate B. SHA-256: `b544ece50dcd97c97a75d0d244e852957e1bc0b07bea287cdcbfe236d9dababd`.
- **V1:** [current-architecture.png](review-case/current-architecture.png), frame 1, entire image; especially the center worker box, right database/backup box, arrowheads and footer. SHA-256: `d4b14a19f591fe906cb66d36d32b62861e38420302ffe10fd2c4af229c15b7a7`.
- **W1:** [AWS Regions — official region table](https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-regions.html), `ap-south-1` and `eu-west-1` rows, accessed 31 October 2026.
The source hashes establish file identity, not the truth of the underlying claims. The short references R, C-A, C-B and V1 resolve directly to the packaged sources above; no external extraction bundle is required to inspect this example.

All supplied text and the full supplied image were reviewed. No other diagrams, contracts, original invoices, load-test artifacts, deployed configurations, tenant-isolation tests, backup configurations or ServiceNow residency evidence were supplied. The review does not infer those documents' contents. No current ServiceNow release, entitlement or pricing claim was needed: the hosted boundary comes directly from R4.

The report establishes A's exclusion under the stated capacity and cost constraints and identifies the evidence required to decide B. It cannot establish B's true throughput, monthly cost, end-to-end residency, production suitability, realized savings or global minimum cost. The recommendation remains conditional until those material gaps are closed.
