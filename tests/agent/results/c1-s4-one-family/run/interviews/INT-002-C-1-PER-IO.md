---
interview_id: INT-002
run_id: agent-c1-s4-one-family
task: C-1
persona: PER-IO
date: 2026-10-30
topics: [user groups, privileges, information release]
---
# INT-002 — C-1 — PER-IO

### Q1 {#INT-002.Q1}
Asked of: PER-IO · Task: C-1
**A1 {#INT-002.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#users]]
> About 25 SOC operators use the alarms, but only in IODS; they never sign in to the gateway.
> They are the reason the system exists.

### Q2 {#INT-002.Q2}
Asked of: PER-IO · Task: C-1
**A2 {#INT-002.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#users]] [[product/architecture.md#identity]]
> Three remote administrators manage configuration, accounts and updates and review logs; about
> ten field technicians work on site through the maintenance port under the shared fieldtech
> account; two ISSO-staff auditors have read-only access. Remote users get the admin or
> auditor role from identity service group claims.

### Q3 {#INT-002.Q3}
Asked of: PER-IO · Task: C-1
**A3 {#INT-002.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/data-flows.md#top]] [[product/conops.md#information]]
> Telemetry leaves only to IODS over the mutually authenticated TLS link, and audit records only
> to the CSSP SIEM. Nothing else is released, and no PII is held beyond user names in account
> and audit records.
