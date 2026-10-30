---
interview_id: INT-071
run_id: example-synthetic-01
task: A-3
persona: PER-ISSO
date: 2026-10-29
topics: [au assessment evidence, audit configuration, log review, attribution]
---
# INT-071 — A-3 — PER-ISSO

### Q1 {#INT-071.Q1}
Asked of: PER-ISSO · Task: A-3 · Control focus: au-2, au-3, au-4, au-5, au-8, au-9, au-12, au-14
Show the audit configuration and sample records on a station.

**A1 {#INT-071.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#dt-1]] [[product/architecture.md#logging]]
> On station 3: the audit policy matches the CSSP-agreed event list; sample records show time,
> component, user, event type, source and outcome, with mission IDs on flight control records
> and source and destination on router denies. Local storage holds 90 days with the 75 percent
> warning set, and pulling the log volume raised the logging-failure alert. Time comes from the
> enclave server, falling back to GDT GPS time. Only the admin role can read or clear local
> logs. Command sessions are recorded start to end and the admin console can watch a live one.
> The GDT generates its events but keeps them in its own log.

### Q2 {#INT-071.Q2}
Asked of: PER-ISSO · Task: A-3 · Control focus: au-6, au-6.3
What log review happens on the station, and what is not reviewed?

**A2 {#INT-071.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#dt-1]] [[product/conops.md#limitations]]
> The enclave reviews forwarded workstation and router records daily once they arrive. My
> weekly station report has run only during test events. GDT and mission planner logs are not
> forwarded, by design today, so they are neither reviewed centrally nor correlated; there is
> no date yet for forwarding them.

### Q3 {#INT-071.Q3}
Asked of: PER-ISSO · Task: A-3 · Control focus: au-10
Can every recorded action be tied to a person?

**A3 {#INT-071.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]]
> CAC users, yes: mission upload, command sessions and product export carry the CAC identity.
> Actions under `gcsmaint` show only the shared account name.
