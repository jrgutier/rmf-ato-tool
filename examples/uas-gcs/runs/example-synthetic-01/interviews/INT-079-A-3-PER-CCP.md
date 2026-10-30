---
interview_id: INT-079
run_id: example-synthetic-01
task: A-3
persona: PER-CCP
date: 2026-10-29
topics: [ir inherited CSSP services, ia inherited directory, ma remote administration origin]
---
# INT-079 — A-3 — PER-CCP

### Q1 {#INT-079.Q1}
Asked of: PER-CCP · Task: A-3 · Control focus: ir-4, ir-4.8, ir-4.13, ir-4.14, ir-5, ir-6, ir-7
What evidence shows the enclave CSSP's incident services are in place for this station?

**A1 {#INT-079.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]]
> The CSSP service agreement lists the station's six test units and the ISSO as station contact.
> A test incident ticket opened through the portal on 2026-10-20 was acknowledged in 35 minutes
> and closed with guidance. The SOC analyzes forwarded workstation and router events and
> enclave intrusion detection data, and correlates them with external reports. The enclave's
> own incident response and continuity inheritance is in its current authorization.

### Q2 {#INT-079.Q2}
Asked of: PER-CCP · Task: A-3 · Control focus: ia-2, ia-4.9, ia-12, ma-4.3
What do the directory and the S6 management enclave provide?

**A2 {#INT-079.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]]
> The brigade directory holds the station role groups and user attributes, and accounts come
> only from CAC holders identity proofed at issuance. Remote administration comes only from S6
> workstations inside the authorized brigade enclave, whose authorization is current.
