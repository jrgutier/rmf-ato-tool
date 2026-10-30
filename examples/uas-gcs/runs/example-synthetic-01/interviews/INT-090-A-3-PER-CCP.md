---
interview_id: INT-090
run_id: example-synthetic-01
task: A-3
persona: PER-CCP
date: 2026-10-29
topics: [ra sa sc inherited policy, enclave-provided services, threat information and hunting]
---
# INT-090 — A-3 — PER-CCP

### Q1 {#INT-090.Q1}
Asked of: PER-CCP · Task: A-3 · Control focus: ra-1, sa-1, sc-1
Show the Component policies the station inherits for these families and their review dates.

**A1 {#INT-090.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]]
> The risk assessment, system and services acquisition, and system and communications protection
> policies and procedures are all published by the Component cybersecurity program; each cover
> page shows a review within the last year, and the program office is on the distribution list.

### Q2 {#INT-090.Q2}
Asked of: PER-CCP · Task: A-3 · Control focus: sa-9, sa-9.1, sa-9.2, sa-9.3, sa-9.8, sc-7, sc-7.25, sc-21, sc-45
Show the evidence for the enclave's part.

**A2 {#INT-090.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#interconnections]]
> The enclave's ATO is current and the station's connection approval names the station, its
> flows (syslog over TLS, LDAPS, remote administration from the S6 subnet) and its uplink. The
> enclave firewall, intrusion detection, validating resolvers and time source are in the enclave's
> own assessed baseline. The enclave is a DoD system hosted in the United States.

### Q3 {#INT-090.Q3}
Asked of: PER-CCP · Task: A-3 · Control focus: ra-3.2, ra-3.3, ra-5.11, ra-10
Show the threat information the station receives and the hunt coverage.

**A3 {#INT-090.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]]
> The CSSP alert distribution list includes the station ISSM, and the alert log shows the weekly
> reviews while stations were connected; the brigade threat assessment and the Component threat
> summaries are on file. Public vulnerability reports come in through the DoD disclosure program.
> The CSSP hunt uses the enclave collector, which holds workstation and router logs only; the
> mission planner and ground data terminal logs never reach it, so the hunt cannot see them.
