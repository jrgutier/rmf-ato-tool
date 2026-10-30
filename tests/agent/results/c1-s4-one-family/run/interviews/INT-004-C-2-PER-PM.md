---
interview_id: INT-004
run_id: agent-c1-s4-one-family
task: C-2
persona: PER-PM
date: 2026-10-30
topics: [INF-02 and INF-03 impact levels]
---
# INT-004 — C-2 — PER-PM

### Q1 {#INT-004.Q1}
Asked of: PER-PM · Task: C-2
**A1 {#INT-004.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-INFOTYPES]] [[product/architecture.md#identity]]
> For INF-02 keep the confidentiality adjustment to moderate: the private keys and firewall rules
> would let someone impersonate a gateway or map paths into the enclave. Integrity moderate and
> availability low as provisioned; a lost unit is replaced from the signed baseline image.

### Q2 {#INT-004.Q2}
Asked of: PER-PM · Task: C-2
**A2 {#INT-004.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-INFOTYPES]] [[product/architecture.md#logging]]
> For INF-03 I confirm moderate, moderate, low. The records are copied to the CSSP within a
> minute, so a local loss is tolerable, but tampering would hide administrative misuse.

### Q3 {#INT-004.Q3}
Asked of: PER-PM · Task: C-2
**A3 {#INT-004.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#information]]
> The only personal data are user names in account and audit records. Nothing is classified.
