# ServiceNow architecture considerations

Use this guidance only when the user is designing on, integrating with, or governing ServiceNow. Verify current official documentation and the actual customer agreement for release-specific behavior, availability, quotas and entitlements. These questions are not universal product or licensing rules.

## Preserve platform boundaries

For ordinary hosted instances, treat ServiceNow infrastructure as managed platform capacity. Do not assume every scoped application has a separately selectable EC2 instance, operating system, database engine, or Kubernetes deployment. Record exceptions only when the deployment agreement supports them.

Distinguish platform applications, integration capabilities, customer-controlled MID hosts, external processing services, and downstream systems. A MID Server is a communication/integration component with its own supported capabilities; it is not a general-purpose substitute for every external worker.

## Model decisions architects can actually make

Consider approved reuse versus extension versus new scoped app; appropriate data ownership and table relationships; entitled connector versus approved custom integration; synchronous versus asynchronous behavior when semantics allow; execution frequency; external processing boundaries; MID placement and supported failover; and support ownership.

Evaluate access controls, integration identity, data exposure, transaction behavior, retries and idempotency. Do not infer that a line in a diagram provides secure communication, supported scaling, or regulatory compliance.

## Commercial and portfolio context

Use actual contract allowances, product subscriptions, usage records, paid integration rules, existing commitments and renewal dates. Distinguish marginal new spend, allocated existing spend, and future avoidable cost. Do not invent a price per application, a license requirement, or a guaranteed saving.

Check overlap with existing Enterprise Architecture, application portfolio, CMDB, asset management and Cloud Cost Management capabilities. Position a new assistant around a demonstrated gap, such as consistent design-time comparison using the organization's own approved patterns. Do not claim existing products lack a feature without checking the relevant release and entitlement.

## Starting official sources

Recheck these when making current factual claims; retain the accessed date and exact page supporting the claim.

- Platform architecture: https://www.servicenow.com/docs/r/platform-administration/how-now-platform-works.html
- MID Server: https://www.servicenow.com/docs/r/servicenow-platform/mid-server/mid-server-landing.html
- Enterprise Architecture: https://www.servicenow.com/products/enterprise-architecture.html
- Cloud Cost Management: https://www.servicenow.com/products/cloud-cost-management.html
- Usage and subscriptions: https://www.servicenow.com/docs/r/integrate-applications/integration-hub/subscription-usage.html
- Entitlements: https://www.servicenow.com/products/entitlements-packages.html

If browsing is unavailable, use the supplied materials and label release-specific facts as unverified. A requirement for fresh verification is not permission to invent a citation.
