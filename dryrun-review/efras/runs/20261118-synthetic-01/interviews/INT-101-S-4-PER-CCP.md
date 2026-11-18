---
interview_id: INT-101
run_id: 20261118-synthetic-01
task: S-4
persona: PER-CCP
date: 2026-11-18
topics: [media sanitization by the cloud region]
---
# INT-101 — S-4 — PER-CCP

### Q1 {#INT-101.Q1}
Asked of: PER-CCP · Task: S-4 · Control focus: mp-6
What does the Example GovCloud IL4 region do to sanitize media, and what is left to EFRAS?
**A1 {#INT-101.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[product/architecture.md#physical]] [[INT-071.A1]] [[INT-076.A1]]
> We sanitize every storage device in our data centers before it is reused, released or
> disposed of, with NSA-approved or FIPS-validated techniques, under the IL4 provisional
> authorization; the assessment report in our package covers it. Tenants never handle our
> media. EFRAS has no physical or removable media of its own. On decommission the program
> deletes its buckets and database and schedules deletion of its keys, which makes any copy left
> on our devices unreadable.
