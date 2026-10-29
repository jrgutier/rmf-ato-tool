---
interview_id: INT-007
run_id: agent-skeleton
task: C-2
persona: PER-IO
date: 2026-10-29
topics: [INF-01 impact values, consequences of compromise, PII and classification]
---
# INT-007 — C-2 — PER-IO

### Q1 {#INT-007.Q1}
Asked of: PER-IO · Task: C-2
**A1 {#INT-007.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-INFOTYPES]] [[product/conops.md#information]]
> INF-01, the sensor telemetry and alarms, is ours, the installation security operations
> organization's. Confidentiality: I confirm moderate. Disclosure shows where our perimeter
> sensing is weak, which is a serious adverse effect on the installation's protection, not a
> catastrophic one.

### Q2 {#INT-007.Q2}
Asked of: PER-IO · Task: C-2
**A2 {#INT-007.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-INFOTYPES]] [[product/conops.md#information]]
> Integrity: I confirm moderate. Tampered telemetry could hide an intrusion or raise false
> alarms; that seriously degrades the SOC's picture. Patrols and other sensors keep it short of
> severe.

### Q3 {#INT-007.Q3}
Asked of: PER-IO · Task: C-2
**A3 {#INT-007.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-INFOTYPES]] [[product/conops.md#availability]] [[product/conops.md#environment]]
> Availability: I confirm low. Losing one site's feed is a limited adverse effect: IODS flags a
> silent site within 5 minutes and the SOC covers it with guard patrols for several days, well
> beyond the 72-hour replacement goal.

### Q4 {#INT-007.Q4}
Asked of: PER-IO · Task: C-2
**A4 {#INT-007.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#information]] [[product/profile.yaml]]
> INF-01 carries no PII: site and sensor identifiers only. We handle it as unclassified; none of
> the material marks it classified. I own no other type on the gateway; INF-02 and INF-03 belong
> to the program, so ask the program manager for those.
