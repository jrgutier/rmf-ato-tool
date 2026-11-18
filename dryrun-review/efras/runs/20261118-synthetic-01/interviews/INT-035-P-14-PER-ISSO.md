---
interview_id: INT-035
run_id: 20261118-synthetic-01
task: P-14
persona: PER-ISSO
date: 2026-11-18
topics: [operational weaknesses, workarounds, most severe component threat, designated risk]
---
# INT-035 — P-14 — PER-ISSO

### Q1 {#INT-035.Q1}
Asked of: PER-ISSO · Task: P-14
**A1 {#INT-035.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#account-review]] [[product/architecture.md#logging]] [[product/conops.md#limitations]]
> Operationally, three workarounds should be in the assessment. The break-glass accounts are
> sealed and alerted, but nobody has rehearsed opening them. Our own audit copy lasts 90 days, so
> any look-back past that depends on ECSSP pulling its copy. And the analyst exports leave the
> system as files I cannot recall once downloaded. The quarterly account review works; the last
> one removed two stale accounts.

### Q2 {#INT-035.Q2}
Asked of: PER-ISSO · Task: P-14
**A2 {#INT-035.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-034.A3]] [[product/data-flows.md#top]]
> The component facing the most severe threat is the database with the readiness API in front of
> it: it holds the aggregated readiness data and all maintainer records, and a nation-state actor
> who reached it would get both. I rate that exfiltration risk moderate, the highest in the
> assessment, so the system's designated risk must be at least moderate.
