---
interview_id: INT-096
run_id: 20261118-synthetic-01
task: S-4
persona: PER-CCP
date: 2026-11-18
topics: [the cloud region's part of backup]
---
# INT-096 — S-4 — PER-CCP

### Q1 {#INT-096.Q1}
Asked of: PER-CCP · Task: S-4 · Control focus: cp-9
What does the Example GovCloud IL4 region implement for backup, and what must EFRAS configure?
**A1 {#INT-096.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[INT-071.A1]]
> The region provides the snapshot and point-in-time recovery machinery for the managed database
> and the durability of object storage, across its availability zones, under its IL4 provisional
> authorization. EFRAS must turn on and set retention for point-in-time recovery and snapshots,
> enable bucket versioning, choose the encryption keys and test its own restores; we do not test
> restores for tenants.
