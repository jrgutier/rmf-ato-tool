---
interview_id: INT-140
run_id: 20261118-synthetic-01
task: I-2
persona: PER-PRIV
date: 2026-11-18
topics: [privacy plan as implemented, PIA status, export pseudonyms]
---
# INT-140 — I-2 — PER-PRIV

### Q1 {#INT-140.Q1}
Asked of: PER-PRIV · Task: I-2 · Control focus: pt-2, pt-3, ra-8, si-12
Does the privacy plan you approved match what was implemented?
**A1 {#INT-140.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-133.A1]] [[product/privacy.md#pia]] [[product/conops.md#limitations]] [[product/test-results.md#pentest]]
> Yes. The ingest field filter keeps only the five SORN data elements, the monthly purge runs,
> and the sign-in banner gives notice, as the plan says. Two things stay as I approved them: the
> PIA is still draft 0.9 and must be signed before production data, and exports keep the
> unsalted DoD ID hash until release 1.6; the red team's PT-2 demonstrated that risk, which the
> plan already names. Nothing in implementation changed the privacy plan's content, but the
> privacy plan is part of this update of the plan set, and I concur with it.
