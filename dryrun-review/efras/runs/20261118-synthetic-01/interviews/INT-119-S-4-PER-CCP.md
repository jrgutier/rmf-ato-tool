---
interview_id: INT-119
run_id: 20261118-synthetic-01
task: S-4
persona: PER-CCP
date: 2026-11-18
topics: [cloud provisional authorization, inheritance documents, contract clauses, provider duties]
---
# INT-119 — S-4 — PER-CCP

### Q1 {#INT-119.Q1}
Asked of: PER-CCP · Task: S-4 · Control focus: cloud (DoD CIO reciprocity guide)
Speaking for Example GovCloud IL4 region: what authorization does the offering hold, under what conditions, and what does EFRAS inherit from?
**A1 {#INT-119.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[INT-071.A1]] [[INT-076.A1]]
> For Example GovCloud IL4 region. A DoD provisional authorization at Impact Level 4, issued by
> DISA through a new cloud authorization process on 2024-09-18. Its conditions: monthly
> continuous monitoring deliverables, an annual assessment, and the customer responsibility
> matrix items stay with each tenant. The package is in eMASS: our security plan, the security
> requirements traceability matrix and the customer responsibility matrix, which say what a
> tenant inherits and what it must configure. We build to the cloud computing SRG and apply the
> STIGs to our managed services. EFRAS uses our platform services: managed Kubernetes, managed
> PostgreSQL, object storage and the key service, on our network and compute.

### Q2 {#INT-119.Q2}
Asked of: PER-CCP · Task: S-4 · Control focus: cloud (DTM 24-001)
What do the enterprise contract and task order say on cybersecurity, and what do you deliver to DoD parties?
**A2 {#INT-119.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-060.A1]] [[product/architecture.md#leveraged]]
> The Component enterprise cloud contract follows DFARS Subpart 239.76, and the EFRAS task order
> inherits its clauses: the accreditation boundary, licensing, notifying the CSSP of incidents,
> threat-representative testing, sharing our CSSP DCO data, a corrective action process,
> inspection access and report delivery. We share our DCO data with the designated CSSP, the AO
> and the DoD sponsor. We report findings on our infrastructure to the CSSP and make incident
> data available to it. We do nothing inside the tenant's workloads.
