---
interview_id: INT-137
run_id: 20261118-synthetic-01
task: I-1
persona: PER-CCP
date: 2026-11-18
topics: [inherited configuration settings, managed services, provider evidence]
---
# INT-137 — I-1 — PER-CCP

### Q1 {#INT-137.Q1}
Asked of: PER-CCP · Task: I-1 · Control focus: cm-6, pe-3, mp-6
Speaking for Example GovCloud IL4 region: how are the inherited configuration settings of the managed Kubernetes control plane and the managed PostgreSQL engine put in place for EFRAS?
**A1 {#INT-137.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-119.A1]] [[product/architecture.md#leveraged]] [[product/test-results.md#stig-scan]]
> For Example GovCloud IL4 region. The Kubernetes control plane and the PostgreSQL engine
> settings a tenant cannot reach are configured by us to the STIGs under our IL4 provisional
> authorization and assessed in our annual assessment; our customer responsibility matrix lists
> them as provider responsibility. EFRAS gets them the same way every tenant does; nothing is
> configured per tenant. The evidence EFRAS can cite is our package in eMASS and our monthly
> continuous monitoring deliverables; we do not hand out per-tenant scan results.
