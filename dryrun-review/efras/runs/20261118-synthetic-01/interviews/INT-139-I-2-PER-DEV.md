---
interview_id: INT-139
run_id: 20261118-synthetic-01
task: I-2
persona: PER-DEV
date: 2026-11-18
topics: [as-built release, inventory versions, recovery and incident mechanisms]
---
# INT-139 — I-2 — PER-DEV

### Q1 {#INT-139.Q1}
Asked of: PER-DEV · Task: I-2 · Control focus: cm-2, cm-8
What is built and deployed now, and does the inventory still match it?
**A1 {#INT-139.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#top]] [[product/test-results.md#pentest]] [[product/test-results.md#pipeline-1-5]] [[product/hw-sw-inventory.md#items]]
> Release 1.5.0 is what the program's inventory lists and what every developer test ran
> against in pre-production. Since then release 1.5.1, of 2026-11-07, fixed the report export
> scoping check (PT-1, retested pass on 2026-11-10) and the verbose server header from the
> dynamic scan. Nothing is in production yet. No item was added or removed: the same sixteen
> items, the same base image 2026.09 and node image 2026.10, the same database version, and
> example-imagelib is still 2.9.1 until 1.5.2. The product inventory still shows 1.5.0 for the
> containers; the pipeline updates the inventory record at the next release tag.

### Q2 {#INT-139.Q2}
Asked of: PER-DEV · Task: I-2 · Control focus: cp-9, cp-10, ir-4
Are the recovery and incident mechanisms the plans name built as written?
**A2 {#INT-139.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#dt-2]] [[product/conops.md#limitations]] [[product/architecture.md#logging]]
> Yes, as far as they have been tested: point-in-time restore to a new instance worked in DT-2
> in 3 h 10 min; the rebuild of the cluster in the second region exists only as templates and has
> never been run; export audit events reach the CSSP within 5 minutes. Nothing about recovery or
> incident handling changed in 1.5.1.
