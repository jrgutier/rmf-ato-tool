---
interview_id: INT-031
run_id: 20261118-synthetic-01
task: P-13
persona: PER-PRIV
date: 2026-11-18
topics: [PII life cycle, dissemination, retention, disposition]
---
# INT-031 — P-13 — PER-PRIV

### Q1 {#INT-031.Q1}
Asked of: PER-PRIV · Task: P-13
**A1 {#INT-031.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/privacy.md#pii]] [[product/data-flows.md#top]] [[ART-BND]]
> As the program walked me through it: maintainer PII is never created in EFRAS. It is collected
> only in the nightly EMIS extract (DF-3), lands in object storage, is validated by the ingest
> worker and stored in the database (DF-5). It is used by the API to show qualification coverage
> per work center and to join actions to people.

### Q2 {#INT-031.Q2}
Asked of: PER-PRIV · Task: P-13
**A2 {#INT-031.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/data-flows.md#top]]
> It leaves the database in two disseminations I worry about: the fleet analysts' exports (DF-7)
> and the training extract to the sandbox (DF-8). Both replace names with an unsalted hash of the
> DoD ID number, so both are still PII until release 1.6 brings salted, rotated pseudonyms. Inside
> the sandbox the data scientists see the extract only.

### Q3 {#INT-031.Q3}
Asked of: PER-PRIV · Task: P-13
**A3 {#INT-031.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/privacy.md#minimization]] [[INT-029.A4]]
> Disposition: the ingest worker purges maintainer PII monthly once its linked maintenance action
> falls outside the 5-year analysis window, which matches the records schedule. What the program
> has not shown me is how long the exported files and the training extract live in object
> storage and the sandbox; I need that before I approve the PIA.

### Q4 {#INT-031.Q4}
Asked of: PER-PRIV · Task: P-13
**A4 {#INT-031.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]] [[INT-029.A2]]
> The user identifiers in the audit records are created by the components themselves at sign-in,
> role change and export, kept 90 days in the log store, and disclosed to ECSSP, which keeps them
> a year under its own agreement. After 90 days the program's copy is deleted.
