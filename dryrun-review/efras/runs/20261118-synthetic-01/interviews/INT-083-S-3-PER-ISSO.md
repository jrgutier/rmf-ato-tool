---
interview_id: INT-083
run_id: 20261118-synthetic-01
task: S-3
persona: PER-ISSO
date: 2026-11-18
topics: [operational side of the allocated controls]
---
# INT-083 — S-3 — PER-ISSO

### Q1 {#INT-083.Q1}
Asked of: PER-ISSO · Task: S-3
Which of the allocated controls do you operate day to day, and on which components?
**A1 {#INT-083.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/architecture.md#logging]] [[product/architecture.md#configuration]] [[INT-055.A1]]
> I provision the application roles in the API and run the quarterly role review (AC-2 on
> CMP-API); I read the weekly report of privileged actions, exports and denied requests from the
> log pipeline (AU-6 on CMP-LOGS, the CSSP doing the round-the-clock part); I get the hourly drift
> scan results and sign off each release before the pipeline deploys it (CM-3 on CMP-K8S); and I
> track the SCAP results against the STIGs (CM-6). The allocation matches what I do; nothing of
> mine is allocated to a component I do not touch.

### Q2 {#INT-083.Q2}
Asked of: PER-ISSO · Task: S-3
Is any control allocated to you that you cannot carry today?
**A2 {#INT-083.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]]
> AU-11: I can only keep 90 days in our store until the archive tier arrives in release 1.6. And
> CP-4: I have no failover test result to show until February. Those are gaps in what we do, not
> in where the controls sit.
