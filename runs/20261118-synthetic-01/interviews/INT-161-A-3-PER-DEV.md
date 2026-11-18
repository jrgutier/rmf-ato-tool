---
interview_id: INT-161
run_id: 20261118-synthetic-01
task: A-3
persona: PER-DEV
date: 2026-11-24
topics: [application container configuration, ASD STIG checklist review, 1.5.2 fixes]
---
# INT-161 — A-3 — PER-DEV

### Q1 {#INT-161.Q1}
Asked of: PER-DEV · Task: A-3 · Control focus: cm-6 (BM-04 review, PRC-009)
For the Application Security and Development STIG review of the five containers: what checklist, settings record or results can you show for each?
**A1 {#INT-161.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#pipeline-1-5]] [[ASM-019]]
> We have never filled in that checklist for any of the five services. What we can show is the
> pipeline record for 1.5.0 and 1.5.1, static, dependency, image and dynamic scans, and the
> build files on the factory's hardened base image. We have no document that states the secure
> settings each container must have, so there is nothing to compare the running containers
> against item by item. The two database items are fixed in our 1.5.2 branch, which waits on
> the factory's new base image for the report service and is planned for 2026-12-10; it has not
> reached pre-production.
