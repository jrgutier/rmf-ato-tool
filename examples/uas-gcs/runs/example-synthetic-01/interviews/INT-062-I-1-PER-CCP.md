---
interview_id: INT-062
run_id: example-synthetic-01
task: I-1
persona: PER-CCP
date: 2026-10-29
topics: [inherited controls, enclave services, audit forwarding]
---
# INT-062 — I-1 — PER-CCP

### Q1 {#INT-062.Q1}
Asked of: PER-CCP · Task: I-1 · Control focus: au-6, ia-2, sc-7
How were the inherited controls put in place for the station?

**A1 {#INT-062.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#dt-1]] [[ART-ORG-CONTEXT]]
> The station's CAC groups exist in the brigade directory and DT-1 showed users outside them
> refused. The enclave collector receives workstation and router logs after reconnect, which
> DT-1 also showed. The planner and ground data terminal logs are not forwarded, so the enclave
> cannot review them; that gap belongs to the system, not to the inherited control.
