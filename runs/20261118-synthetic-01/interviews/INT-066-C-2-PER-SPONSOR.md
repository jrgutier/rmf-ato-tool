---
interview_id: INT-066
run_id: 20261118-synthetic-01
task: C-2
persona: PER-SPONSOR
date: 2026-11-18
topics: [business processes against the availability impact, criticality analysis Assess iteration]
---
# INT-066 — C-2 — PER-SPONSOR

### Q1 {#INT-066.Q1}
Asked of: PER-SPONSOR · Task: C-2
The availability impact of the categorization is low. You rated the disruption of BP-01, BP-02
and BP-03 low at P-8. Does any process need more than a low availability impact?
**A1 {#INT-066.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-018.A1]] [[INT-018.A2]] [[product/conops.md#availability]]
> No. BP-01, daily readiness reporting, is the most sensitive, and it tolerates 72 hours before
> we fall back to manual EMIS reports; that is a limited effect. Forecasting and fleet analysis
> tolerate a week. None of the three exceeds low, so the categorization and the analysis agree
> and I have nothing to reevaluate. The program's own 24-hour recovery objective is a target,
> not a reason to raise availability.

### Q2 {#INT-066.Q2}
Asked of: PER-SPONSOR · Task: C-2
Do you agree with adding the ingest worker, the database and the key management service to the
critical items, after EMIS and the identity broker?
**A2 {#INT-066.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-065.A4]] [[INT-018.A4]]
> Yes. Without the nightly load nothing I care about is current, and without the database
> nothing is shown at all. I leave the order of the components to the ISSM.
