---
interview_id: INT-018
run_id: agent-skeleton
task: S-4
persona: PER-CCP
date: 2026-10-29
topics: [ia-2 shared responsibility, sc-7 shared responsibility, provider evidence]
---
# INT-018 — S-4 — PER-CCP

### Q1 {#INT-018.Q1}
Asked of: PER-CCP · Task: S-4 · Control focus: ia-2
**A1 {#INT-018.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[product/architecture.md#leveraged]] [[product/architecture.md#interconnections]]
> For the Installation ICAM Service: we issue and manage the identities, validate the DoD PKI
> credential and run the account workflow for remote ESG users, and we assert the identity and
> group claim to the console. That is covered by the enclave ATO of 2025-11-20 and the installation
> service agreement for IC-2. ESG must configure its federation with us, map our claims to its
> roles, and refuse anyone we have not authenticated. We do nothing for local accounts on the
> maintenance port; those are entirely ESG's.

### Q2 {#INT-018.Q2}
Asked of: PER-CCP · Task: S-4 · Control focus: sc-7
**A2 {#INT-018.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[product/architecture.md#leveraged]] [[product/architecture.md#network]]
> For the Installation Network Enclave: the enclave firewall in front of every site switch, the
> intrusion detection and the network access control are ours, under the enclave ATO of
> 2025-11-20. We place ESG on its own enclave VLAN and permit at the enclave edge only the flows
> the program registered: telemetry to IODS, syslog to the CSSP and console HTTPS from the
> management VLAN. ESG must run its own host firewall to the same rules and tell us before any new
> flow.
