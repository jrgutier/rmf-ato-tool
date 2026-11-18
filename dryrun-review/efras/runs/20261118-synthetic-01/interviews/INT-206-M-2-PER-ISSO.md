---
interview_id: INT-206
run_id: 20261118-synthetic-01
task: M-2
persona: PER-ISSO
date: 2027-02-01
topics: [operations evidence since the last assessment, drift, scans, roll-up]
---
# INT-206 — M-2 — PER-ISSO

### Q1 {#INT-206.Q1}
Asked of: PER-ISSO · Task: M-2 · Control focus: cm-2, cm-3
Show the drift and change records since the assessment. Can a change still reach the account outside the pipeline?
**A1 {#INT-206.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/monitoring/cycle-2026-11.md#drift]] [[INT-203.A2]]
> The drift record I can show runs to 2026-11-15: 360 hourly scans of pre-production and one
> event, the console security group change of 2026-11-04, flagged within the hour and reverted by
> the pipeline. So the detection works. But yes, a change can still reach the account outside the
> pipeline: the cloud operations engineers' console role can write security groups in both
> accounts. The engineer did not raise an emergency change; nobody reviewed or approved it before
> it was made. After 2026-11-15 I have no drift summary to hand you.

### Q2 {#INT-206.Q2}
Asked of: PER-ISSO · Task: M-2 · Control focus: cm-6, cm-8
Has the SCAP STIG scan run since the SCA's scan of 2026-11-23, and was the inventory reviewed at release 1.6?
**A2 {#INT-206.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/monitoring/cycle-2026-11.md#top]] [[INT-202.A2]]
> No STIG scan result after 2026-11-23 is in the records I handed over; the cycle's records hold
> the image and node scans only. The inventory record shows release 1.6 since the M-1 update of
> 2027-02-01, with which environment runs what; I cannot show you a review record dated at the
> release itself, 2027-01-15.

### Q3 {#INT-206.Q3}
Asked of: PER-ISSO · Task: M-2 · Control focus: ra-5
What do the scans show?
**A3 {#INT-206.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/monitoring/cycle-2026-11.md#vuln-scan]]
> The factory's nightly rescan and the provider's node scan of 2026-11-14: the two highs in
> efras-report (example-imagelib) still open, waiting on the base image; one new medium in the
> web framework runtime (INV-016), first reported on that scan, with a fix planned in release
> 1.5.2, which never shipped. Nodes: no high or critical. I have no scan record showing whether
> release 1.6 carried the INV-016 fix.

### Q4 {#INT-206.Q4}
Asked of: PER-ISSO · Task: M-2 · Control focus: ca-5, ca-7
Where is the monthly roll-up?
**A4 {#INT-206.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/monitoring/cycle-2026-11.md#top]] [[ART-CONMON]] [[ART-POAM]]
> There is none yet. The records of 2026-11-01 to 2026-11-15 are the summaries the strategy's
> sources produce; I have not compiled a monthly roll-up from the dashboard and the tracker, and
> nothing for December or January has gone to the PM, the ISSM or the AODR. The first roll-up
> is the POAM-024 milestone due 2027-02-28. The POA&M itself is in eMASS with one monthly update,
> 2027-01-15, as the R-3 record says.
