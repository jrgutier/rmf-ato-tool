---
interview_id: INT-043
run_id: 20261118-synthetic-01
task: P-15
persona: PER-PRIV
date: 2026-11-18
topics: [privacy requirements, Privacy Act rules, PIA, agreement]
---
# INT-043 — P-15 — PER-PRIV

### Q1 {#INT-043.Q1}
Asked of: PER-PRIV · Task: P-15
Which privacy requirements must EFRAS meet beyond the privacy control baseline?
**A1 {#INT-043.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-RA]] [[product/privacy.md#minimization]]
> There are three, matching the risk assessment. First, under OMB A-130 and the FIPPs, data is
> treated as non-PII only after effective de-identification. That means salted, rotated
> pseudonyms in exports and the training extract. Each export type also gets a minimization
> review with my office, and records beyond the 5-year window are purged monthly. Second, the
> Privacy Act and the SORN. Third, under DoDI 5400.16, the PIA must be approved before
> production use with real PII, and updated at each major change.

### Q2 {#INT-043.Q2}
Asked of: PER-PRIV · Task: P-15
How does each Privacy Act rule that no control states apply to EFRAS?
**A2 {#INT-043.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/privacy.md#pii]] [[product/privacy.md#authority]]
> - Direct collection does not apply. EFRAS collects nothing from individuals. All PII comes from
>   the EMIS extract, and EMIS is the collecting system.
> - The disclosure bar applies. No record leaves EFRAS without consent except under the SORN's
>   routine uses or the Act's exceptions.
> - The First Amendment bar applies. EFRAS must hold no record of how anyone exercises First
>   Amendment rights. The extract has no such field, and none may be added.
> - Access and appeals apply. EFRAS sends every access or amendment request to my office, which
>   handles appeals under DoD 5400.11-R. EFRAS corrects records only through EMIS.
> - Rules of conduct and penalties apply to everyone who handles the records, including ERST
>   staff.
> - Contract provisions: ERST contractors operate the cluster and the database that hold the
>   records. I want the Privacy Act clauses in the ERST task order, whatever the categorization
>   record says.
> One requirement, REQ-15, carries all of these.

### Q3 {#INT-043.Q3}
Asked of: PER-PRIV · Task: P-15
Do the requirements address your office's needs?
**A3 {#INT-043.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/privacy.md#pia]]
> Yes: REQ-14, REQ-15 and REQ-16. I agreed on 2026-11-18. The PIA is still a draft, so REQ-16 is
> a requirement the system does not yet meet.
