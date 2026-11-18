---
interview_id: INT-044
run_id: 20261118-synthetic-01
task: P-15
persona: PER-UR
date: 2026-11-18
topics: [operational requirements, availability, usability, agreement]
---
# INT-044 — P-15 — PER-UR

### Q1 {#INT-044.Q1}
Asked of: PER-UR · Task: P-15
Which operational needs must the security requirements respect?
**A1 {#INT-044.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#availability]] [[product/conops.md#users]]
> We need the dashboards back within a day of an outage and never more than 72 hours late. Sign-in
> has to stay CAC only, with no extra passwords. A few of our people use screen readers, so the
> pages must work with assistive technology. I judge the need met when a restore test shows
> yesterday's data back within 24 hours.

### Q2 {#INT-044.Q2}
Asked of: PER-UR · Task: P-15
Do the requirements address that?
**A2 {#INT-044.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-BIA]]
> Yes: REQ-06 for recovery, REQ-01 for CAC sign-in and REQ-12 for accessibility. I agreed on
> 2026-11-18. I know the regional failover has never been tested.
