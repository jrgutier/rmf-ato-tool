---
interview_id: INT-042
run_id: 20261118-synthetic-01
task: P-15
persona: PER-IO
date: 2026-11-18
topics: [loss concerns, export release rules, agreement]
---
# INT-042 — P-15 — PER-IO

Respondent: fleet maintenance data steward (information owner of maintenance and readiness data,
maintainer PII, forecasts and reports).

### Q1 {#INT-042.Q1}
Asked of: PER-IO · Task: P-15
Which losses of your data concern you most, and what would show you they are prevented?
**A1 {#INT-042.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-INFOTYPES]] [[product/conops.md#limitations]]
> I am most concerned about loss of integrity of the maintenance and readiness data, and then
> about disclosure of maintainer records. I want three things. Every change to stored data must
> come from the ingest or a logged administrator action. Records must be encrypted where they are
> stored and when they move. A de-identified export must really be de-identified: nobody holding
> a list of DoD ID numbers can re-identify a person. Today that last one fails (limitation 1),
> so I rank it the top privacy need until release 1.6.

### Q2 {#INT-042.Q2}
Asked of: PER-IO · Task: P-15
Do the requirements address those concerns?
**A2 {#INT-042.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-RA]]
> Yes, with REQ-03 for encryption, REQ-04 and REQ-05 for integrity and the change record, REQ-09
> for marking, and REQ-14 for de-identification. I agreed on 2026-11-18. Release 1.6 must
> deliver REQ-14 before exports reach production users.
