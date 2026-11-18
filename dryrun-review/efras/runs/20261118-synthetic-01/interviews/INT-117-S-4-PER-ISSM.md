---
interview_id: INT-117
run_id: 20261118-synthetic-01
task: S-4
persona: PER-ISSM
date: 2026-11-18
topics: [cloud offering leveraged authorization, provider agreements, agreement validation]
---
# INT-117 — S-4 — PER-ISSM

### Q1 {#INT-117.Q1}
Asked of: PER-ISSM · Task: S-4 · Control focus: pe-3, mp-6, si-2, cp-9
How should the leveraged authorization of the Example GovCloud IL4 region be recorded, given that EFRAS inherits PE-3 and MP-6 from it whole?
**A1 {#INT-117.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[INT-060.A1]] [[INT-071.A1]] [[INT-079.A1]]
> As what it is: a commercial cloud service offering with a DoD provisional authorization at
> IL4, an IT service authorized outside our organization that we use under the enterprise cloud
> contract and our task order. We inherit its controls through its customer responsibility
> matrix and its security plan in eMASS: PE-3 and MP-6 whole, SI-2 and CP-9 in part. That makes
> it an external service whose package we review, not one of our organization's own common
> control providers, although P-5 lists it among the providers of common controls and S-3
> allocates PE-3 and MP-6 to it as common. I reviewed its package today: provisional
> authorization of 2024-09-18, IL4, monthly continuous monitoring deliverables current, no open
> condition that touches EFRAS. The region hosts every EFRAS component, so a failure or a
> compromise of the region's infrastructure affects the whole system; the maintainer PII sits
> encrypted under our own keys, which limits what the provider's staff can see.

### Q2 {#INT-117.Q2}
Asked of: PER-ISSM · Task: S-4 · Control focus: sa-9
Which agreement documents each provider EFRAS inherits from, and how did you check them?
**A2 {#INT-117.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[INT-060.A3]] [[INT-110.A1]] [[INT-080.A1]]
> One record per provider. The CSSP: its support agreement ECSSP-SA-ARSPO-01 of 2026-04-01. The
> cloud region: the Component enterprise cloud contract and the EFRAS task order. The access
> point and the software factory: their service-level agreements. The Component privacy office:
> no agreement of its own; the Component's privacy program issuance assigns it the SORN, the
> privacy training and the review of PII processing. I checked each on 2026-11-18 for the roles,
> the responsibilities on both sides, the scope and the controls it covers, and listed the
> controls we inherit from each provider under the matching service. The AODR approved each
> instrument as part of the inheritance determination at S-3.
