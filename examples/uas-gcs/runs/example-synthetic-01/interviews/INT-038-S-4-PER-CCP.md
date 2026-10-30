---
interview_id: INT-038
run_id: example-synthetic-01
task: S-4
persona: PER-CCP
date: 2026-10-29
topics: [ac family, inherited policy, enclave account management]
---
# INT-038 — S-4 — PER-CCP

### Q1 {#INT-038.Q1}
Asked of: PER-CCP · Task: S-4 · Control focus: ac-1, ac-2
What do the common control providers deliver for access control?

**A1 {#INT-038.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-035.A1]] [[product/architecture.md#leveraged]]
> The Component cybersecurity program issues the access control policy and procedures and
> reviews them on its own cycle; the station follows them. The Brigade Tactical Network Enclave,
> under its ATO of 2025-05-30, runs the brigade directory: it creates, disables and removes CAC
> accounts and group memberships on S6 request. The station must keep its local accounts, map
> the groups to roles and keep working from cached credentials while disconnected.
