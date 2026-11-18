---
interview_id: INT-077
run_id: 20261118-synthetic-01
task: S-2
persona: PER-PM
date: 2026-11-18
topics: [acceptance of the tailoring, cost and schedule trade-offs]
---
# INT-077 — S-2 — PER-PM

### Q1 {#INT-077.Q1}
Asked of: PER-PM · Task: S-2
Which cost, schedule or performance trade-offs did you weigh in deciding how the controls are implemented?
**A1 {#INT-077.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/architecture.md#logging]] [[product/architecture.md#identity]] [[ART-REQ]]
> Three. Audit retention: an archive tier for a year of our own logs costs storage and a release;
> I funded it for release 1.6 rather than rely on the CSSP's copy, so AU-11 stays and is late, not
> waived. Break-glass: the provider console cannot federate when the identity broker is down, so
> we keep two sealed FIDO2 accounts instead of building our own console federation; IA-2 stays and
> the AO accepts the deviation. Supply chain: we take the software factory's scanning, signing and
> base images instead of running our own pipeline security; it is cheaper and stronger, and the
> price is waiting on the factory for the base image fix.

### Q2 {#INT-077.Q2}
Asked of: PER-PM · Task: S-2
Do you accept the tailoring decisions and their cost?
**A2 {#INT-077.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-074.A2]] [[INT-074.A4]]
> Yes. Nothing removed, nothing compensated, the values as the ISSM set them. The archive tier and
> the pseudonym fix are in the release 1.6 budget, and the restore and failover tests in the
> sustainment line for February.
