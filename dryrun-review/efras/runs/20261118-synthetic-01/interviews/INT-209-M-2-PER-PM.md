---
interview_id: INT-209
run_id: 20261118-synthetic-01
task: M-2
persona: PER-PM
date: 2027-02-01
topics: [triage of the new finding, changes that affect what is due]
---
# INT-209 — M-2 — PER-PM

### Q1 {#INT-209.Q1}
Asked of: PER-PM · Task: M-2 · Control focus: cm-3
The ongoing assessment found that a console change can bypass change control (FND-025). How significant is it to you, and where does it go?
**A1 {#INT-209.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-203.A2]] [[INT-206.A1]] [[ART-RA]]
> Low, as the assessor rates it: the drift scan caught it within the hour and the pipeline undid
> it, and pre-production holds synthetic data. But it is not inconsequential: the same role exists
> in the production account, and the risk assessment's configuration risk (RSK-004) is exactly
> settings drifting outside the baseline. It goes to the POA&M; the fix is a read-only console
> role for network settings with a break-glass path, which ERST can ship in the next release.

### Q2 {#INT-209.Q2}
Asked of: PER-PM · Task: M-2
Did anything change in the cycle that alters what the assessor should look at?
**A2 {#INT-209.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-202.A1]] [[INT-202.A2]] [[ART-CHG]]
> Release 1.6 is the change, in pre-production only. The records after 2026-11-15 are missing, so
> please assess what the records show and say plainly what they do not; COND-01 and COND-05 are
> where the fixes get verified.
