---
interview_id: INT-162
run_id: 20261118-synthetic-01
task: A-3
persona: PER-ISSE
date: 2026-12-02
topics: [contingency plan status, restore re-performance, failover and exercise, backup settings]
---
# INT-162 — A-3 — PER-ISSE

### Q1 {#INT-162.Q1}
Asked of: PER-ISSE · Task: A-3 · Control focus: cp-2
Show me the contingency plan, its contact list, its approval and the list of people and organizations it went to.
**A1 {#INT-162.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-CP]] [[product/conops.md#limitations]] [[product/conops.md#availability]]
> The plan is version 1.0 draft in the program repository, readable only by program staff and changed
> only by merge. It has the essential function, the 24-hour objectives, the restoration order,
> the roles with the on-call roster's names and numbers, the fallback to EMIS reports, the CSSP
> ticket path for incidents and restoration from the templates. The PM has not yet reviewed or
> approved it; the S-6 approval asks for that by 2026-12-15. It has not been sent to the on-call
> engineers, the ISSO, the ISSM, EMIS or the CSSP, so no change to it has been communicated
> either, and no annual review has happened. No contingency training or real event has happened.

### Q2 {#INT-162.Q2}
Asked of: PER-ISSE · Task: A-3 · Control focus: cp-4, cp-9
Today we re-performed the DT-2 restore. What else has been tested, and how are backups configured and protected?
**A2 {#INT-162.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#dt-2]] [[product/conops.md#limitations]] [[product/architecture.md#components]]
> The point-in-time restore you watched today finished well inside the 24-hour objective, close
> to DT-2's 3 h 10 min, and I reviewed the result with you. That restore is the only test there
> has ever been: no regional failover of the cluster and no tabletop; both are planned for
> 2027-02. The restore needed no corrective action. Point-in-time recovery is on for the
> database with daily snapshots encrypted under our own keys, the buckets are versioned with
> deletion protection, and the templates, manifests and documents are in version control, so
> every merge is a copy.
