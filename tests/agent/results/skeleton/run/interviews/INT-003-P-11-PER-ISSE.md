---
interview_id: INT-003
run_id: agent-skeleton
task: P-11
persona: PER-ISSE
date: 2026-10-29
topics: [boundary edge, interfaces, permitted flows, external dependencies]
---
# INT-003 — P-11 — PER-ISSE

### Q1 {#INT-003.Q1}
Asked of: PER-ISSE · Task: P-11
**A1 {#INT-003.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#boundary]] [[ART-INV]]
> The edge is the installation network switch port each gateway's uplink plugs into. Inside are
> the six components the inventory points to: CMP-GW-HW, CMP-GW-OS, CMP-COLLECTOR, CMP-WEBUI,
> CMP-STORE and CMP-SENSOR-NET. Every site's unit uses the same baseline, so all sites are one
> system, not one boundary per site.

### Q2 {#INT-003.Q2}
Asked of: PER-ISSE · Task: P-11
**A2 {#INT-003.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]]
> Three interfaces. The uplink on the enclave VLAN carries outbound TLS 1.3 to IODS, outbound
> syslog over TLS to the CSSP, and inbound HTTPS to the console from the management VLAN only;
> the host firewall denies everything else both ways. The maintenance port is off unless a
> technician turns the shelter key switch, serves only the console on a link-local address, and
> does not route to the uplink. The field radio is a paired, encrypted link; sensor nodes have
> no IP and cannot reach the uplink.

### Q3 {#INT-003.Q3}
Asked of: PER-ISSE · Task: P-11
**A3 {#INT-003.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/data-flows.md#top]] [[product/data-flows.md#telemetry]]
> Seven flows: DF-1 node to collector over the paired radio; DF-2 collector to the buffer on the
> encrypted data partition; DF-3 collector to IODS over TLS 1.3 with mutual certificates; DF-4
> audit records to the CSSP SIEM over syslog/TLS; DF-5 admin workstation to the console over
> HTTPS; DF-6 console to the identity service over TLS with signed assertions; DF-7 technician
> laptop to the console over the maintenance port with a local sign-in. DF-3 through DF-6 cross
> the boundary; DF-7 enters it from an on-site laptop.

### Q4 {#INT-003.Q4}
Asked of: PER-ISSE · Task: P-11
**A4 {#INT-003.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#components]] [[product/architecture.md#interconnections]] [[product/architecture.md#leveraged]]
> We depend on four things outside: IODS (CMP-IODS) receives the telemetry under an
> interconnection agreement; the installation ICAM service (CMP-ICAM) authenticates remote
> administrators; the enclave (CMP-ENCLAVE) enforces the same flows at the enclave edge plus
> intrusion detection and network access control; and the CSSP (CMP-CSSP) collects and watches
> our logs. All four have their own authorizations, so they stay outside the boundary. The
> technician laptop and admin workstation are installation assets, not ours.

### Q5 {#INT-003.Q5}
Asked of: PER-ISSE · Task: P-11
**A5 {#INT-003.A5}** respondent: simulated · tag: SIMULATED · basis: [[product/profile.yaml]] [[product/architecture.md#updates]]
> Our own components are still in engineering and manufacturing development; release 2.2 adds
> remote update, so call them under development. The four external services are operating.
