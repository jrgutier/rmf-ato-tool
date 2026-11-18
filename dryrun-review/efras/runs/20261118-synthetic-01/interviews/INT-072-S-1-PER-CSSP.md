---
interview_id: INT-072
run_id: 20261118-synthetic-01
task: S-1
persona: PER-CSSP
date: 2026-11-18
topics: [CSSP services offered for inheritance, shared responsibility]
---
# INT-072 — S-1 — PER-CSSP

### Q1 {#INT-072.Q1}
Asked of: PER-CSSP · Task: S-1
Speaking for Example Cybersecurity Service Provider: which controls in EFRAS's selected set does your service cover, fully or in part, and under which authorization?
**A1 {#INT-072.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-013.A4]] [[product/architecture.md#leveraged]] [[product/architecture.md#logging]]
> For the Example Cybersecurity Service Provider. SI-4, AU-6, IR-4, IR-6 and RA-5, every one of
> them partial. We monitor the logs you forward around the clock, correlate them against our use
> cases and alert you; we support incident handling and receive your incident reports; we send
> vulnerability alerts and run our external scans. We see only what you send us. Your team
> reviews its own logs weekly, handles the incident on its side, reports to us on time and scans
> and patches inside the account. The service runs under our own ATO, and the ARSPO service
> agreement is dated 2026-04-01.

### Q2 {#INT-072.Q2}
Asked of: PER-CSSP · Task: S-1
Do you keep a copy of the forwarded audit records the system could rely on for retention?
**A2 {#INT-072.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]] [[product/conops.md#limitations]]
> We keep what you forward for one year, for our own analysis. That copy is ours; it is not your
> archive. AU-11 retention stays with the program, and your 90-day store is short of the
> Component's one year.
