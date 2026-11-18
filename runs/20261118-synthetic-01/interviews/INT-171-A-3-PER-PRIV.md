---
interview_id: INT-171
run_id: 20261118-synthetic-01
task: A-3
persona: PER-PRIV
date: 2026-12-07
topics: [SORN elements against ingested fields, re-identification of exports, PIA status]
---
# INT-171 — A-3 — PER-PRIV

### Q1 {#INT-171.Q1}
Asked of: PER-PRIV · Task: A-3 · Control focus: pt-2
What documents the authority for EFRAS's processing, and which data elements does it cover?
**A1 {#INT-171.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/privacy.md#authority]] [[product/privacy.md#pii]]
> The Component's maintenance-records authority, cited in the existing SORN for aviation
> maintenance records; I confirmed its coverage of EFRAS by e-mail on 2026-08-19, and the draft
> PIA cites it. It covers name, DoD ID number, rate or rank, qualifications and work-center
> assignment, received from EMIS and used to show qualification coverage and join actions to
> people. Nothing else is authorized, and EFRAS collects nothing from individuals.

### Q2 {#INT-171.Q2}
Asked of: PER-PRIV · Task: A-3 · Control focus: pt-3
Is the use of the analysts' exports and the training extract within the purposes the SORN and the PIA give?
**A2 {#INT-171.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/test-results.md#pentest]] [[product/privacy.md#pia]]
> Only if they are de-identified, and they are not yet: the unsalted hash of the DoD ID number
> lets anyone with a list of ID numbers re-identify the records, as the red team showed with 50
> numbers. That is my open item on the PIA. The purposes themselves are documented and public in
> the SORN, and the change board brings every PII change to my representative. Salted, rotated
> pseudonyms in release 1.6 (2027-01-15) are the fix I am waiting for.

### Q3 {#INT-171.Q3}
Asked of: PER-PRIV · Task: A-3 · Control focus: ra-8
Where does the PIA stand, and when was it begun relative to development?
**A3 {#INT-171.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/privacy.md#pia]] [[ART-PIA]]
> Version 0.9 of 2026-09-30 is with my office. Development started well before it was drafted.
> I review it on 2027-01-20 and the CIO approves it on 2027-01-25, before any production data
> flows; it will not be approved while the export item is open. The pilot runs on synthetic data,
> so no real maintainer PII has been processed yet.
