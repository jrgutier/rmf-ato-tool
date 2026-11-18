---
interview_id: INT-108
run_id: 20261118-synthetic-01
task: S-4
persona: PER-CSSP
date: 2026-11-18
topics: [vulnerability alerts and external scans]
---
# INT-108 — S-4 — PER-CSSP

### Q1 {#INT-108.Q1}
Asked of: PER-CSSP · Task: S-4 · Control focus: ra-5
What does the CSSP do for vulnerability monitoring of EFRAS, and what does it expect back?
**A1 {#INT-108.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-072.A1]] [[product/architecture.md#leveraged]] [[INT-098.A1]]
> We send vulnerability alerts and directed actions when a new vulnerability affects the
> products EFRAS reports in its inventory, and we run a monthly external scan of the EFRAS
> edge from the access point side. We cannot scan inside the cloud account. We expect the
> program to acknowledge an alert within one working day, to report its remediation status on
> the ticket, and to tell us when a directed action cannot meet its deadline, so that we can
> brief the AO's office. We share what we learn across the systems we serve.
