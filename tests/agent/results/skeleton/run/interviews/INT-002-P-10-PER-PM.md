---
interview_id: INT-002
run_id: agent-skeleton
task: P-10
persona: PER-PM
date: 2026-10-29
topics: [asset priority, planned items, items from other programs]
---
# INT-002 — P-10 — PER-PM

### Q1 {#INT-002.Q1}
Asked of: PER-PM · Task: P-10
**A1 {#INT-002.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/hw-sw-inventory.md#priority]] [[INT-001.A1]]
> The gateway and its software come first: INV-001 to INV-004 are high. If a gateway is lost or
> its software is corrupted, the whole site goes dark or, worse, reports false alarms to the
> SOC. The sensor nodes, their firmware, the radio firmware and the buffer database are
> moderate: one dead node is a coverage gap, and the buffer only matters while IODS is down.

### Q2 {#INT-002.Q2}
Asked of: PER-PM · Task: P-10
**A2 {#INT-002.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#updates]]
> Nothing new is fielded beyond what the developer listed. The one planned change is remote
> update over the uplink in release 2.2; that is a feature of the existing software, not a new
> asset, and it is not delivered yet.

### Q3 {#INT-002.Q3}
Asked of: PER-PM · Task: P-10
**A3 {#INT-002.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#boundary]] [[product/architecture.md#leveraged]]
> The program owns and funds only the gateways and the sensor nodes. IODS, the identity
> service, the enclave and the CSSP belong to other programs with their own authorizations;
> they are not our assets and should not be on our inventory.
