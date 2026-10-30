---
interview_id: INT-006
run_id: agent-skeleton
task: C-1
persona: PER-IO
date: 2026-10-30
topics: [user groups, privileges, information use]
---
# INT-006 — C-1 — PER-IO

### Q1 {#INT-006.Q1}
Asked of: PER-IO · Task: C-1
Who uses the system's outputs, and do they touch the system itself?
**A1 {#INT-006.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#users]] [[product/conops.md#mission]]
> The SOC operators, about 25 of them, are the consumers. They see ESG alarms only in IODS and
> never sign in to ESG. Operators act on alarms through other systems.

### Q2 {#INT-006.Q2}
Asked of: PER-IO · Task: C-1
Which user groups have access to the system, and with what privileges?
**A2 {#INT-006.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#users]] [[product/architecture.md#identity]]
> Three groups sign in to the console. Three system administrators work remotely with full
> privilege over configuration, accounts and updates and review logs. About ten field
> technicians work on site through the maintenance port, also privileged, to replace sensors,
> re-pair radios and run diagnostics. Two auditors from the ISSO staff have read-only remote
> access to audit logs and configuration reports. A sealed break-glass account exists for
> emergencies only.

### Q3 {#INT-006.Q3}
Asked of: PER-IO · Task: C-1
Can you tell who did what with the information on the system?
**A3 {#INT-006.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]]
> For remote users, yes, because each signs in with their own PKI credential. Not for field
> technicians: they share the `fieldtech` account, so the records cannot tell one technician
> from another. That worries me, because a technician can change what sensors report.

### Q4 {#INT-006.Q4}
Asked of: PER-IO · Task: C-1
How does information leave the system?
**A4 {#INT-006.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/data-flows.md#top]] [[product/conops.md#information]]
> Telemetry and alarms go only to IODS, and audit records go to the CSSP's SIEM. Nothing else
> leaves. The only personal data are user names in account and audit records.
