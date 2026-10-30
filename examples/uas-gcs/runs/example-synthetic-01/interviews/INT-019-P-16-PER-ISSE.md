---
interview_id: INT-019
run_id: example-synthetic-01
task: P-16
persona: PER-ISSE
date: 2026-10-29
topics: [enterprise architecture, shared services]
---
# INT-019 — P-16 — PER-ISSE

### Q1 {#INT-019.Q1}
Asked of: PER-ISSE · Task: P-16
**A1 {#INT-019.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-BND]] [[product/architecture.md#interconnections]] [[product/architecture.md#leveraged]]
> In the enterprise architecture ETGCS is a mission system at the tactical edge. It sits behind
> the Brigade Tactical Network Enclave, which gives it the brigade directory, log collection,
> boundary protection and incident response as shared services (IC-2), and it feeds the brigade
> intelligence system (IC-1). It uses no cloud service and no other shared service.

### Q2 {#INT-019.Q2}
Asked of: PER-ISSE · Task: P-16
**A2 {#INT-019.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-REQ]] [[ART-INV]]
> The architecture already places most requirements: the enclave carries directory, logging and
> boundary functions; the station carries everything that must work disconnected. The gap is that
> the planner and GDT logs never reach the enclave, so the requirement for full audit coverage
> needs a forwarding path inside the station.
