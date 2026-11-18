---
interview_id: INT-165
run_id: 20261118-synthetic-01
task: A-3
persona: PER-ISSO
date: 2026-11-20
topics: [incident handling walk-through, incident reporting records, nonlocal maintenance records]
---
# INT-165 — A-3 — PER-ISSO

### Q1 {#INT-165.Q1}
Asked of: PER-ISSO · Task: A-3 · Control focus: ir-4
Walk me through how a suspected incident would be handled today, step by step, and show me what you would work from at each step.
**A1 {#INT-165.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-IRP]] [[product/test-results.md#dt-2]] [[product/conops.md#limitations]]
> The CSSP's ticket reaches me and the ISSM; I open the program record and page the on-call
> engineer. Containment comes from the operations runbook: isolate the workload with a network
> policy, revoke the workload identity or console role, or block the source at the edge.
> Eradication and recovery are a redeploy from signed images and the templates, or the
> database point-in-time restore that DT-2 tested. That runbook and the on-call roster are what
> we have. The incident response plan is still a draft waiting for the PM's approval due
> 2026-12-15, so nobody has been trained on it and I cannot say the handling follows an
> approved plan. Its tie to contingency planning is only on paper: both plans are drafts and
> neither has been exercised. No incident and no exercise has happened, so there are no
> lessons learned and no after-action report.

### Q2 {#INT-165.Q2}
Asked of: PER-ISSO · Task: A-3 · Control focus: ir-6
Show me where the one-hour reporting duty is stated to users and engineers, and any record of a report made under it.
**A2 {#INT-165.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-IRP]] [[INT-098.A2]]
> The duty and the CSSP operations center contact are on the sign-in banner page and in the
> runbook's reporting section, and the annual awareness module covers it; the training records
> you sampled under at-2 show the module completed. No real incident has been reported. The
> only reports so far are the CSSP's tickets for the scheduled penetration test windows, which I
> acknowledged within the hour, and the notice the CSSP sends to the AO's office through the
> AODR follows its own procedure.

### Q3 {#INT-165.Q3}
Asked of: PER-ISSO · Task: A-3 · Control focus: ma-4
Show me the records of nonlocal maintenance sessions for the last month and how you learn of a manual change.
**A3 {#INT-165.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#configuration]] [[product/architecture.md#logging]]
> Every console session shows in the cloud account activity log and every cluster command in the
> cluster audit log, both in the log store. Diagnostic console sessions are announced in the
> operations channel beforehand. The hourly drift scan reports any manual change to me; in the
> last month it reported none outside an announced session.
