---
interview_id: INT-001
run_id: agent-skeleton
task: P-10
persona: PER-DEV
date: 2026-10-29
topics: [hardware and software items, versions, firmware, component mapping]
---
# INT-001 — P-10 — PER-DEV

### Q1 {#INT-001.Q1}
Asked of: PER-DEV · Task: P-10
**A1 {#INT-001.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/hw-sw-inventory.md#items]]
> The configuration-item list is complete for release 2.1.4: the ERD-400 appliance rev C, the
> ESG OS image 2.1.4, esg-collector 2.1.4, esg-console 2.1.4, EmbedStore 5.3, the ERD radio
> firmware 4.0.2, the ESW-20 sensor node rev B and the ESW node firmware 1.9.0. Those are the
> versions on every fielded unit today, INV-001 through INV-008.

### Q2 {#INT-001.Q2}
Asked of: PER-DEV · Task: P-10
**A2 {#INT-001.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#components]] [[product/hw-sw-inventory.md#items]]
> Mapping to components: the appliance and its radio firmware are CMP-GW-HW; the OS image is
> CMP-GW-OS, and it carries the host firewall and the audit daemon, so those are not separate
> items; the collector is CMP-COLLECTOR, the console CMP-WEBUI, EmbedStore CMP-STORE; the
> sensor nodes and their firmware are CMP-SENSOR-NET.

### Q3 {#INT-001.Q3}
Asked of: PER-DEV · Task: P-10
**A3 {#INT-001.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#updates]] [[product/architecture.md#configuration]]
> Nothing else is installed. The nightly configuration check is part of the OS image, not a
> separate package. One caveat on versions: we publish a signed bundle every month, but units
> are only updated at the quarterly site visits, so a given site can run one bundle behind
> the current one until its next visit.

### Q4 {#INT-001.Q4}
Asked of: PER-DEV · Task: P-10
**A4 {#INT-001.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/hw-sw-inventory.md#hostnames]] [[product/architecture.md#network]]
> Gateways are physical units named `esg-<site>-01`; none is virtual and none is reachable from
> the internet. Sensor nodes have no IP stack and no hostname; they only talk to their gateway
> over the paired radio link.
