---
interview_id: INT-047
run_id: 20261118-synthetic-01
task: P-16
persona: PER-ISSE
date: 2026-11-18
topics: [external connections, DISN connection approval, DODIN position, cross-domain]
---
# INT-047 — P-16 — PER-ISSE

### Q1 {#INT-047.Q1}
Asked of: PER-ISSE · Task: P-16
How does EFRAS attach to the DODIN, and what approval does that connection need?
**A1 {#INT-047.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/conops.md#environment]]
> EFRAS is on the DODIN. Its one attachment to the DISN is through the Example Enterprise Cloud
> Access Point (ECAP) to NIPRNet. That is HTTPS on 443 inbound to the load balancer, TLS 1.2 or
> 1.3, carrying CUI readiness views and exports. The production account goes through the DISA
> cloud connection process. We submitted the production connection request on 2026-10-15
> (fictional request reference CCP-EFRAS-PROD), and it is still requested, not approved. The
> pre-production account connected under the same process earlier. EFRAS crosses no security
> domain: everything is unclassified, and there is no mission partner connection.

### Q2 {#INT-047.Q2}
Asked of: PER-ISSE · Task: P-16
What are the other external connections, and how are they reached?
**A2 {#INT-047.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#interconnections]] [[product/data-flows.md#top]]
> All the others are reached through the cloud and the ECAP attachment, over the egress
> allow-list. None is its own DISN connection, so none needs a separate DISA approval.
> - Cloud region: the provider's service APIs over its private endpoints (HTTPS 443). It carries
>   all EFRAS data at rest and in processing, CUI with PII. Bidirectional.
> - Identity broker: SAML/OIDC over HTTPS 443, signed assertions with the DoD ID number and
>   groups. Bidirectional.
> - EMIS: a nightly pull over mutual TLS on 443 of the signed, checksummed extract, with
>   maintenance actions and maintainer PII (CUI). Inbound.
> - Supply status service: a nightly API pull over TLS on 443 of supply status (CUI). Inbound.
> - Software factory: registry pulls and the deploy role over HTTPS 443, bringing signed images
>   and templates. Inbound.
> - CSSP: log forwarding over TLS on 443, sending audit records with user identifiers (CUI).
>   Outbound.
> The EMIS agreement and the supply service-level agreement are interconnection agreements
> between the two systems. They are not DoD connection approvals.
