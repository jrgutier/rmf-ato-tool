---
interview_id: INT-005
run_id: example-synthetic-01
task: P-5
persona: PER-CISO
date: 2026-10-29
topics: [common control providers, inheritance]
---
# INT-005 — P-5 — PER-CISO

### Q1 {#INT-005.Q1}
Asked of: PER-CISO · Task: P-5
**A1 {#INT-005.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[product/stakeholders.md#roles]]
> For aviation systems on the brigade network the published provider is the Brigade Tactical
> Network Enclave, run by the brigade S6. Its ATO is dated 2025-05-30. It offers enclave
> boundary protection and intrusion detection, the brigade directory for CAC user accounts,
> central log collection and review, and incident response support.

### Q2 {#INT-005.Q2}
Asked of: PER-CISO · Task: P-5
**A2 {#INT-005.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-005.A1]] [[product/architecture.md#identity]] [[product/architecture.md#logging]]
> Every enclave control is offered in part only, because each tactical system keeps its own
> boundary device and local accounts: sc-7 and si-4 at the enclave boundary, ac-2 and ia-2 for
> CAC users in the directory, au-6 and au-9 for logs that reach the collector, and ir-4 and
> ir-6 for incident handling and reporting. The system still owns its local part of each.

### Q3 {#INT-005.Q3}
Asked of: PER-CISO · Task: P-5
**A3 {#INT-005.A3}** respondent: simulated · tag: SIMULATED · basis: [[ASM-004]]
> The Component itself provides the organization-wide program management controls (the pm
> family) and the policy parts of each family's first control, under the Component CISO's own
> program. Systems inherit those fully. The Component privacy program provides the privacy
> program controls; there are no privacy common controls a non-PII system needs beyond that.
