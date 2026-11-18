---
interview_id: INT-049
run_id: 20261118-synthetic-01
task: P-16
persona: PER-SPONSOR
date: 2026-11-18
topics: [enterprise architecture placement, mission area]
---
# INT-049 — P-16 — PER-SPONSOR

### Q1 {#INT-049.Q1}
Asked of: PER-SPONSOR · Task: P-16
Where does EFRAS sit in the enterprise architecture, and what does that mean for its security?
**A1 {#INT-049.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#mission]] [[ART-ORG-CONTEXT]]
> EFRAS is a business-support capability in the Component's aviation logistics and readiness
> portfolio. It sits downstream of EMIS, the system of record, and of the supply status service.
> It is a read-only consumer: it never writes back. It feeds readiness views and briefing
> slides to the fleet. In the security architecture it is a tenant of the Component's IL4
> cloud, behind the enterprise access point and identity broker, and monitored by the
> Component CSSP. It adds no new enterprise service. Its risk is the risk of a business system
> in that portfolio.
