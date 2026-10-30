---
interview_id: INT-012
run_id: agent-skeleton
task: S-1
persona: PER-CCP
date: 2026-10-30
topics: [common controls, inheritance, provider authorization]
---
# INT-012 — S-1 — PER-CCP

### Q1 {#INT-012.Q1}
Asked of: PER-CCP · Task: S-1
Which common controls may ESG inherit, and fully or in part?
**A1 {#INT-012.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[product/architecture.md#components]]
> All three offers are partial. The Installation Network Enclave provides boundary protection at
> the enclave edge for sc-7; ESG keeps its host firewall. The Installation ICAM Service provides
> DoD PKI authentication for remote administrators under ia-2; ESG federates its console to it.
> The CSSP collects and correlates events in the SIEM for au-2; ESG must generate and forward them.

### Q2 {#INT-012.Q2}
Asked of: PER-CCP · Task: S-1
What is each provider's authorization status?
**A2 {#INT-012.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]]
> The enclave holds a current ATO, and the ICAM service is covered by it. The CSSP holds a
> current authorization. Nothing we offer depends on a pending decision.
