---
interview_id: INT-003
run_id: agent-skeleton
task: P-11
persona: PER-ISSE
date: 2026-10-30
topics: [boundary edge, interfaces, permitted flows, external dependencies]
---
# INT-003 — P-11 — PER-ISSE

### Q1 {#INT-003.Q1}
Asked of: PER-ISSE · Task: P-11
Which components share the ESG boundary, and where is its edge?
**A1 {#INT-003.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#boundary]] [[ART-INV]]
> Inside are the six components the inventory maps to: CMP-GW-HW, CMP-GW-OS, CMP-COLLECTOR,
> CMP-WEBUI, CMP-STORE and CMP-SENSOR-NET. Every site unit runs the same baseline, so all
> units are one system. The edge is the installation network switch port that the gateway's
> uplink plugs into; the maintenance port and the field radio are internal interfaces.

### Q2 {#INT-003.Q2}
Asked of: PER-ISSE · Task: P-11
Which interfaces and flows does the design permit?
**A2 {#INT-003.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/data-flows.md#top]]
> On the uplink: outbound TLS 1.3 with mutual certificates to IODS, outbound syslog over TLS
> to the CSSP SIEM, TLS to the identity service for sign-in, and inbound HTTPS to the console
> from the management VLAN only. The host firewall denies everything else by default. The
> maintenance port is off until the shelter key switch enables it, serves only the console on
> a link-local address and does not route to the uplink. Sensor nodes reach only their paired
> gateway over the encrypted radio and have no IP path anywhere.

### Q3 {#INT-003.Q3}
Asked of: PER-ISSE · Task: P-11
What does ESG rely on outside its boundary?
**A3 {#INT-003.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#components]] [[product/architecture.md#interconnections]] [[product/architecture.md#leveraged]]
> Four things: IODS, which receives the telemetry under an interconnection agreement and has
> its own ATO; the installation ICAM service for PKI sign-in; the network enclave for the
> enclave firewall, intrusion detection and network access control; and the CSSP for SIEM
> collection, monitoring and incident response. All four are separately authorized and
> nothing of ours runs on them.

### Q4 {#INT-003.Q4}
Asked of: PER-ISSE · Task: P-11
How is data protected inside the boundary?
**A4 {#INT-003.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/data-flows.md#telemetry]] [[product/data-flows.md#top]]
> The radio link is paired and encrypted, and the collector drops messages from unpaired
> nodes and malformed messages. The collector writes to the buffer locally, and the buffer
> lives on the encrypted data partition.
