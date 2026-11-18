---
interview_id: INT-032
run_id: 20261118-synthetic-01
task: P-13
persona: PER-PM
date: 2026-11-18
topics: [life cycle of program-owned types, landing files, exports, report cache, keys]
---
# INT-032 — P-13 — PER-PM

### Q1 {#INT-032.Q1}
Asked of: PER-PM · Task: P-13
**A1 {#INT-032.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/data-flows.md#main]] [[product/architecture.md#components]]
> The extract files in the object storage landing zone are kept for seven days after a successful
> load so a failed night can be replayed, then a bucket lifecycle rule deletes them. Report
> exports and the report cache expire after 30 days; the signed download links last minutes.
> Supply status is replaced each night and its history kept with the linked maintenance records
> for the same 5-year window.

### Q2 {#INT-032.Q2}
Asked of: PER-PM · Task: P-13
**A2 {#INT-032.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/privacy.md#minimization]] [[ASM-009]]
> Analyst exports in object storage expire with the 30-day report cache; once a user downloads
> one, it follows that user's CUI handling, as any export does. The training extract is replaced
> each time the data scientists retrain the model, and the previous extract is deleted. The
> product material does not write these periods down; I will give them to the privacy officer in
> writing with the PIA.

### Q3 {#INT-032.Q3}
Asked of: PER-PM · Task: P-13
**A3 {#INT-032.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#configuration]] [[product/architecture.md#components]]
> The security information is created by the pipeline from the infrastructure templates and in
> the key service, used by every component, maintained by key rotation and template changes, and
> disposed of by scheduled key deletion when a key is retired. Audit records: created by every
> component, collected by the log pipeline, stored 90 days, forwarded to ECSSP, then deleted.
