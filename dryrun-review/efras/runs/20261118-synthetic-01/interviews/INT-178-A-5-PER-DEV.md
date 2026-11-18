---
interview_id: INT-178
run_id: 20261118-synthetic-01
task: A-5
persona: PER-DEV
date: 2026-12-14
topics: [technical changes since the assessment, new scan or test results]
---
# INT-178 — A-5 — PER-DEV

### Q1 {#INT-178.Q1}
Asked of: PER-DEV · Task: A-5 · Control focus: si-2
Has release 1.5.2 or any other change reached pre-production since the out-brief?
**A1 {#INT-178.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[INT-172.A1]]
> No. The 1.5.2 branch carries the two PostgreSQL settings and the rebuilt report container, but
> the report container cannot be built until the factory publishes the hardened base image with
> the fixed example-imagelib, and we ship the release as one. There is no new scan result.

### Q2 {#INT-178.Q2}
Asked of: PER-DEV · Task: A-5 · Control focus: sc-7
Is there a retest result for the sandbox egress allow-list change of 2026-11-03?
**A2 {#INT-178.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#pentest]] [[ASM-022]]
> No. We narrowed the allow-list on 2026-11-03 and our own notebook check no longer reaches the
> public mirror, but that is our check, not the red team's retest, and I have no record of it
> the assessor could re-perform. The red team retest is still pending.
