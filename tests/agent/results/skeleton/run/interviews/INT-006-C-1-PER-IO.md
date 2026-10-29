---
interview_id: INT-006
run_id: agent-skeleton
task: C-1
persona: PER-IO
date: 2026-10-29
topics: [users of outputs, user groups and privileges, information leaving the system]
---
# INT-006 — C-1 — PER-IO

### Q1 {#INT-006.Q1}
Asked of: PER-IO · Task: C-1
**A1 {#INT-006.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#users]] [[product/conops.md#mission]]
> The people who rely on the telemetry are the roughly 25 SOC operators. They read ESG alarms
> in IODS and never sign in to a gateway, so they have no logical access to the system itself;
> they still depend on what it sends being complete and correct.

### Q2 {#INT-006.Q2}
Asked of: PER-IO · Task: C-1
**A2 {#INT-006.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#users]] [[product/architecture.md#identity]]
> Three groups touch the console. The 3 system administrators sign in remotely with DoD PKI
> through the identity service in the `admin` role and manage configuration, accounts, updates
> and logs. The 2 auditors from the ISSO staff sign in the same way in the read-only `auditor`
> role to review audit logs and configuration reports. About 10 field technicians sign in on
> site through the maintenance port with the shared `fieldtech` local account to replace
> sensors, re-pair radios and run diagnostics. I want it on record that technician actions
> cannot be attributed to a person today; that is a disclosed limitation.

### Q3 {#INT-006.Q3}
Asked of: PER-IO · Task: C-1
**A3 {#INT-006.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/data-flows.md#top]] [[product/architecture.md#logging]]
> Telemetry leaves only to IODS over TLS with mutual certificates. Audit records leave only to
> the CSSP SIEM. Nothing else is exported; the buffer holds telemetry only until IODS takes it.
