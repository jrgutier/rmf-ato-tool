---
interview_id: INT-015
run_id: agent-c1-s4-one-family
task: S-4
persona: PER-CCP
date: 2026-10-30
topics: [inherited parts, provider evidence]
---
# INT-015 — S-4 — PER-CCP

### Q1 {#INT-015.Q1}
Asked of: PER-CCP · Task: S-4
**A1 {#INT-015.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[product/architecture.md#network]]
> The enclave firewall in front of each site switch permits only the documented ESG flows and the
> management VLAN path to the console, and network access control admits only the registered ESG
> port; its ATO is dated 2025-11-20. The ICAM service authenticates remote users with DoD PKI,
> runs the account workflow, and disables accounts on request. ESG must keep its host firewall
> rules and the console's claim mapping consistent with ours.

### Q2 {#INT-015.Q2}
Asked of: PER-CCP · Task: S-4
**A2 {#INT-015.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[product/architecture.md#logging]]
> The CSSP, authorized 2026-01-30, correlates ESG events in the SIEM and alerts the ISSO on
> anomalous sign-ins and remote sessions. ESG must generate and forward the agreed events; the
> authorization letters of both providers are available to the assessor.
