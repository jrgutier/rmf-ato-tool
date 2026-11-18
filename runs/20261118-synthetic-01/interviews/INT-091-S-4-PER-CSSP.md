---
interview_id: INT-091
run_id: 20261118-synthetic-01
task: S-4
persona: PER-CSSP
date: 2026-11-18
topics: [the CSSP's part of audit review and retention]
---
# INT-091 — S-4 — PER-CSSP

### Q1 {#INT-091.Q1}
Asked of: PER-CSSP · Task: S-4 · Control focus: au-6, au-11
What does the CSSP do with EFRAS's forwarded logs, and what must EFRAS do itself?
**A1 {#INT-091.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]] [[product/architecture.md#leveraged]] [[INT-072.A1]] [[INT-072.A2]]
> We take the forwarded stream in near real time, correlate it 24x7 against our use cases, and
> open a ticket to the EFRAS ISSO and ISSM for anything we see; we keep the records one year under
> the service agreement. We cannot see application meaning, so the weekly application-level
> review stays with the ISSO, and our one-year copy does not satisfy the program's own retention
> duty: it is our copy for our analysis, not one the program controls.
