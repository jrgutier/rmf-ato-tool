---
interview_id: INT-026
run_id: 20261118-synthetic-01
task: P-11
persona: PER-AO
date: 2026-11-18
topics: [boundary confirmation, separately authorized services, boundary conditions, boundary identifier]
---
# INT-026 — P-11 — PER-AO

### Q1 {#INT-026.Q1}
Asked of: PER-AO · Task: P-11
**A1 {#INT-026.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-025.A1]] [[product/architecture.md#boundary]]
> Yes. As the AODR briefed it to me, the boundary is the program-owned production account and the
> twelve components the program configures in it. That is the set I will authorize. The
> pre-production account stays outside; if real data ever goes there, it comes back to me.

### Q2 {#INT-026.Q2}
Asked of: PER-AO · Task: P-11
**A2 {#INT-026.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[product/architecture.md#interconnections]]
> The cloud region, the access point, the software factory and the CSSP each have their own
> authorization or agreement, and EMIS, the supply status service and the identity broker are
> separately authorized systems. I will not take their risk into this boundary; I take the
> risk of the connections to them, which is why the unsigned EMIS agreement matters to me.

### Q3 {#INT-026.Q3}
Asked of: PER-AO · Task: P-11
**A3 {#INT-026.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/profile.yaml]] [[INT-025.A1]]
> The boundary identifier is EFRAS-BND-1. One condition: any new interconnection or any component
> moved into or out of the production account is a boundary change that the ISSM brings to the
> AODR before it is made.
