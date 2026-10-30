---
interview_id: INT-001
run_id: agent-cold-start-resume
task: P-10
persona: PER-DEV
date: 2026-10-30
topics: [item list, versions, firmware, component mapping]
---
# INT-001 — P-10 — PER-DEV

### Q1 {#INT-001.Q1}
Asked of: PER-DEV · Task: P-10
Is the ESG hardware and software list complete? Is anything installed on a unit that the list omits?
**A1 {#INT-001.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/hw-sw-inventory.md#items]] [[product/architecture.md#components]]
> The list is complete for what we install: eight configuration items, INV-001 through
> INV-008. The host firewall and the local audit daemon are part of the ESG OS image
> (INV-002), not separate items, and the configuration-check job is a scheduled task in that
> image too. Nothing else is installed on the appliance or the sensor nodes.

### Q2 {#INT-001.Q2}
Asked of: PER-DEV · Task: P-10
Which versions are installed on the fielded test units today?
**A2 {#INT-001.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/hw-sw-inventory.md#items]] [[product/conops.md#limitations]]
> The baseline is release 2.1.4 for the OS image, collector and console, EmbedStore 5.3,
> radio firmware 4.0.2 and node firmware 1.9.0. Because units are only updated at quarterly
> site visits, a unit can lag the latest monthly bundle; the operations team, not my team,
> knows which bundle each unit runs right now.

### Q3 {#INT-001.Q3}
Asked of: PER-DEV · Task: P-10
On which component does each item run?
**A3 {#INT-001.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#components]] [[product/hw-sw-inventory.md#items]]
> The appliance hardware and its radio module firmware are CMP-GW-HW; the OS image is
> CMP-GW-OS; esg-collector is CMP-COLLECTOR; esg-console is CMP-WEBUI; EmbedStore is
> CMP-STORE; the sensor nodes and their firmware are CMP-SENSOR-NET. IODS, the identity
> service, the enclave and the CSSP are other systems; nothing of ours is installed there.

### Q4 {#INT-001.Q4}
Asked of: PER-DEV · Task: P-10
Are any items virtual or reachable from the public internet, and how are units named?
**A4 {#INT-001.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/hw-sw-inventory.md#hostnames]]
> All units are physical appliances named `esg-<site>-01`, for example `esg-north-01`. None
> is virtual and none is reachable from the public internet. Sensor nodes have no IP address
> and no hostname.
