---
interview_id: INT-012
run_id: example-synthetic-01
task: P-11
persona: PER-ISSE
date: 2026-10-29
topics: [interfaces, permitted flows, segmentation, external dependencies]
---
# INT-012 — P-11 — PER-ISSE

### Q1 {#INT-012.Q1}
Asked of: PER-ISSE · Task: P-11
**A1 {#INT-012.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#boundary]] [[product/architecture.md#components]]
> The boundary is one station kit: the workstation with its image and three applications, the
> GDT, the router and the air vehicle data link endpoint. The edge is the router's uplink port.
> The airframe itself is covered by airworthiness, not by our boundary.

### Q2 {#INT-012.Q2}
Asked of: PER-ISSE · Task: P-11
**A2 {#INT-012.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]]
> Inside, the workstation, the GDT management port and the router share one isolated segment,
> and the GDT management web service listens only there. The router uplink permits outbound TLS
> to the brigade intelligence system's product drop, syslog over TLS to the enclave collector,
> LDAPS to the brigade directory, and inbound remote administration from the S6 management
> subnet only; everything else is denied both ways. The aircraft link is encrypted radio with
> per-mission keys and is never routed to the uplink.

### Q3 {#INT-012.Q3}
Asked of: PER-ISSE · Task: P-11
**A3 {#INT-012.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/data-flows.md#top]]
> We rely on two things outside: the Brigade Tactical Network Enclave for directory,
> boundary protection, log collection and incident support, and the brigade intelligence system
> as the receiver of products. Nine data flows, DF-1 to DF-9, cover everything; the weak one
> inside is DF-9, where the GDT is configured over HTTPS with a single vendor administrator
> password, and the removable-media path DF-8 relies on bundle signatures.
