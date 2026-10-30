---
interview_id: INT-004
run_id: agent-skeleton
task: P-11
persona: PER-AO
date: 2026-10-30
topics: [boundary confirmation, external systems]
---
# INT-004 — P-11 — PER-AO

### Q1 {#INT-004.Q1}
Asked of: PER-AO · Task: P-11
Is the set of gateway and sensor components, across all sites, the system you will authorize?
**A1 {#INT-004.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-003.A1]] [[product/architecture.md#boundary]]
> Yes. I will authorize the gateway appliances with their software and the paired sensor nodes
> at every site as one system, because they share one baseline and one program owner. A unit
> that departs from the approved baseline is not covered until the program brings it back.

### Q2 {#INT-004.Q2}
Asked of: PER-AO · Task: P-11
Do you agree that IODS, the ICAM service, the enclave and the CSSP stay outside the boundary?
**A2 {#INT-004.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-003.A3]] [[product/architecture.md#interconnections]] [[product/architecture.md#leveraged]]
> Agreed. Each has its own authorization, so they are external. ESG may rely on their controls
> only as far as their authorizations cover them. Use ESG-BND-1 as the boundary identifier.

### Q3 {#INT-004.Q3}
Asked of: PER-AO · Task: P-11
Do you set any condition on the boundary?
**A3 {#INT-004.A3}** respondent: simulated · tag: SIMULATED · basis: [[INT-003.A2]] [[product/architecture.md#network]]
> The maintenance port must stay inside the boundary and must not route to the uplink. Any new
> interface or flow out of the boundary comes back to me before it is enabled.
