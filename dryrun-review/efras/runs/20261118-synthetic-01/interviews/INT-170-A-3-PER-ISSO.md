---
interview_id: INT-170
run_id: 20261118-synthetic-01
task: A-3
persona: PER-ISSO
date: 2026-12-01
topics: [leaver handling against the out-processing checklists, monthly purge log]
---
# INT-170 — A-3 — PER-ISSO

### Q1 {#INT-170.Q1}
Asked of: PER-ISSO · Task: A-3 · Control focus: ps-4 (leaver timing, PRC-004)
For the same ten leavers, show me the out-processing checklist steps beyond the EFRAS account: CAC revocation, the exit briefing, returned property and what happened to their exports.
**A1 {#INT-170.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#account-review]] [[ASM-020]] [[INT-152.A3]]
> The squadrons completed all ten checklists: each shows the CAC turned in to the security
> office and the supervisor's exit briefing signed, with the CUI and PII handling topics ticked.
> None of the ten held a privileged access workstation, a FIDO2 key or a console role. Their
> exports stay in object storage, readable by me and the information owner. The EFRAS account is
> the gap you already have from the ac-2 test: no checklist records a notification time to me,
> and the two leavers of the 2026-10-06 review were removed only at the review.

### Q2 {#INT-170.Q2}
Asked of: PER-ISSO · Task: A-3 · Control focus: si-12
Show me the purge log for the last three months and your monthly checks of it.
**A2 {#INT-170.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/privacy.md#minimization]] [[ART-PIA]]
> The ingest worker writes a purge entry each month with the cut-off date of the five-year
> window and the number of records removed; in pre-production the synthetic records are seeded
> with old dates, so each run removes some. My monthly sign-off is on each entry. The report
> cache bucket has a 30-day lifecycle rule.
