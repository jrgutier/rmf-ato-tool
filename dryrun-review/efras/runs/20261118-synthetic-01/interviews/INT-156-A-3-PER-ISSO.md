---
interview_id: INT-156
run_id: 20261118-synthetic-01
task: A-3
persona: PER-ISSO
date: 2026-11-20
topics: [event list and its review, weekly log review records, log store protection, retention]
---
# INT-156 — A-3 — PER-ISSO

### Q1 {#INT-156.Q1}
Asked of: PER-ISSO · Task: A-3 · Control focus: au-2
Show me the event list, the record of its coordination with the CSSP and its last review.
**A1 {#INT-156.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]] [[ART-SSP]]
> The event list is a table in the runbook with the source, event type and reason for each entry;
> the reason column is the rationale for after-the-fact investigation. The CSSP's onboarding
> ticket of 2026-04-22 shows its use cases asked for the export, privileged and failed
> authorization events, and the list includes them. I reviewed it for release 1.5 on 2026-06-15;
> the next review is due with release 1.6.

### Q2 {#INT-156.Q2}
Asked of: PER-ISSO · Task: A-3 · Control focus: au-6
Show me the weekly review reports, the pager alert history and the CSSP tickets for the last three months, and what you did with each finding.
**A2 {#INT-156.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]] [[ART-SSP]]
> Thirteen weekly reports from 2026-08-17 to 2026-11-09 are on file, each signed off by me; two
> noted export volume above the usual range, which I traced to month-end briefing exports and
> reported to the ISSM in the weekly note. The pager history shows those two volume alerts and no
> break-glass alert. The CSSP opened three tickets in the period, all scan noise from the
> pipeline's dynamic scan, each closed with the window notice. When the CSSP raised the threat
> level for one week in 2026-09, the review ran daily; the daily reports for that week are on
> file. No possible misuse of PII arose, so nothing went to the privacy office.

### Q3 {#INT-156.Q3}
Asked of: PER-ISSO · Task: A-3 · Control focus: au-9, au-11
Show me the log store's retention and access policy and its change alerts, and the oldest record each store holds today.
**A3 {#INT-156.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]] [[product/conops.md#limitations]]
> The log store's buckets have a 90-day write-once lock; the read policy allows only my role and
> the auditor role, and no role has delete. A policy change raises an alert to me and the ISSM;
> the alert history shows only the change that set the lock in 2026-03. Each store holds records
> back 90 days and no further, because the lock expires and the lifecycle rule deletes them. The
> program's one-year copy waits on the archive tier in release 1.6; for older records we depend
> on the CSSP's copy.
