---
interview_id: INT-002
run_id: agent-skeleton
task: P-10
persona: PER-PM
date: 2026-10-30
topics: [asset priority, planned items]
---
# INT-002 — P-10 — PER-PM

### Q1 {#INT-002.Q1}
Asked of: PER-PM · Task: P-10
Which ESG assets matter most to the mission, and why?
**A1 {#INT-002.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/hw-sw-inventory.md#priority]] [[product/conops.md#mission]]
> The gateway and its software come first: INV-001 to INV-004. If one of them is lost or
> corrupted, a whole site stops reporting or, worse, reports false readings to the SOC. The
> sensor nodes, their firmware, the radio firmware and the buffer are moderate: one bad node
> leaves a gap, and the buffer only matters while IODS is unreachable.

### Q2 {#INT-002.Q2}
Asked of: PER-PM · Task: P-10
Is anything planned but not yet fielded that should be on the inventory?
**A2 {#INT-002.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/conops.md#program]]
> No new hardware is planned. Release 2.2 (planned for 2026-12) adds remote update and release
> 2.3 (planned for 2027-03) adds per-technician accounts; both are new versions of the same
> software items, not new items. Today twelve pre-production units are installed at test
> sites; sixty are planned for fielding after the decision.

### Q3 {#INT-002.Q3}
Asked of: PER-PM · Task: P-10
Are any items supplied or operated by other programs?
**A3 {#INT-002.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[product/architecture.md#interconnections]]
> The enclave network, the identity service, the CSSP and IODS belong to the installation and
> are separately authorized. My program funds and controls only the gateways and the sensor
> nodes.
