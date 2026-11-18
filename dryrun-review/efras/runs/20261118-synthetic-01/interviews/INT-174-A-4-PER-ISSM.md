---
interview_id: INT-174
run_id: 20261118-synthetic-01
task: A-4
persona: PER-ISSM
date: 2026-12-11
topics: [accuracy of the findings, fixes already under way]
---
# INT-174 — A-4 — PER-ISSM

### Q1 {#INT-174.Q1}
Asked of: PER-ISSM · Task: A-4
Is any fact in the 24 findings wrong?
**A1 {#INT-174.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#top]] [[product/conops.md#limitations]]
> No. I checked each finding against our records at the out-brief. The STIG items, the scan
> dates, the penetration test results and the plan versions are as we hold them. FND-009 is
> right that the inventory still shows release 1.5.0.

### Q2 {#INT-174.Q2}
Asked of: PER-ISSM · Task: A-4
Which findings were already being fixed during the assessment?
**A2 {#INT-174.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#pentest]] [[product/conops.md#limitations]] [[INT-173.A3]]
> PT-3: the allow-list was narrowed on 2026-11-03, but the red team has not retested it, so
> FND-023 is still open. The 1.5.2 items wait on the factory's base image. The EMIS agreement is
> under legal review with a signature target of 2026-12-31. Nothing else was changed during the
> assessment window; the plan approvals come on 2026-12-15.

### Q3 {#INT-174.Q3}
Asked of: PER-ISSM · Task: A-4 · Control focus: ac-2
Do you accept FND-001 and FND-017 on the leaver timing?
**A3 {#INT-174.A3}** respondent: simulated · tag: SIMULATED · basis: [[INT-152.A3]] [[product/test-results.md#account-review]]
> Yes. Nobody tells the account manager when a maintainer leaves a squadron; we only catch it at
> the inactivity disable or the quarterly review. I want a timestamped step on the squadrons'
> out-processing checklist, and I need the squadrons' agreement for it.
