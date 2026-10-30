---
interview_id: INT-011
run_id: agent-c1-s4-one-family
task: S-3
persona: PER-ISSE
date: 2026-10-30
topics: [component allocation, access control capabilities]
---
# INT-011 — S-3 — PER-ISSE

### Q1 {#INT-011.Q1}
Asked of: PER-ISSE · Task: S-3
**A1 {#INT-011.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/architecture.md#components]]
> Accounts, roles, sign-in, lockout and session handling live in the admin web console
> (CMP-WEBUI); the OS (CMP-GW-OS) enforces file and service privileges and generates the audit
> records. Remote identity proofing, PKI authentication and the account workflow come from the
> Installation ICAM Service, so those account controls are hybrid with the console's role mapping
> and local accounts as our part.

### Q2 {#INT-011.Q2}
Asked of: PER-ISSE · Task: S-3
**A2 {#INT-011.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/data-flows.md#management]]
> Flow enforcement is the host firewall on CMP-GW-OS plus the collector's acceptance rules, backed
> by the enclave firewall. Remote access enters only through the console from the management VLAN,
> and the enclave is the managed access point in front of it. Radio pairing and encryption are on
> the gateway radio module, the collector and the sensor nodes.

### Q3 {#INT-011.Q3}
Asked of: PER-ISSE · Task: S-3
**A3 {#INT-011.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#boundary]] [[product/architecture.md#interconnections]]
> Policy, external-system use and interconnection limits have no single component home; allocate
> them to the system as a whole. The buffer database (CMP-STORE) has no user query interface;
> only the collector reads and writes it. ESG has no public content, no security labels, no
> user-to-user sharing, and no mobile devices of its own: technician laptops are installation
> assets outside the boundary.
