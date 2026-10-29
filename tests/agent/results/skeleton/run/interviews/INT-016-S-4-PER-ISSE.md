---
interview_id: INT-016
run_id: agent-skeleton
task: S-4
persona: PER-ISSE
date: 2026-10-29
topics: [authentication design, boundary protection, managed interfaces]
---
# INT-016 — S-4 — PER-ISSE

### Q1 {#INT-016.Q1}
Asked of: PER-ISSE · Task: S-4 · Control focus: ia-2
**A1 {#INT-016.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/conops.md#users]]
> Remote administrators and auditors authenticate to the console through the installation
> identity service with their DoD PKI smart card. The console trusts the identity service's
> assertion, takes the user's unique identity from it, and maps the group claim to the `admin` or
> `auditor` role. Every console session and every action in it runs under that identity, so the
> audit events name the person. The break-glass account `esgadmin` is a single named account kept
> sealed in the program office safe, and each use is logged and reported.

### Q2 {#INT-016.Q2}
Asked of: PER-ISSE · Task: S-4 · Control focus: ia-2
**A2 {#INT-016.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]]
> The design does not meet unique identification on the maintenance port. Field technicians all
> sign in with the shared local `fieldtech` account and its shared password, because some
> maintenance tasks have no network path to the identity service. The console cannot tell the ten
> technicians apart, so processes started in those sessions run as `fieldtech`, not as a person.
> Release 2.3 (planned 2027-03) replaces it with per-technician local accounts and smart-card
> login that works without the identity service.

### Q3 {#INT-016.Q3}
Asked of: PER-ISSE · Task: S-4 · Control focus: sc-7
**A3 {#INT-016.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/architecture.md#boundary]]
> The external managed interface is the uplink port to the site switch. The gateway host firewall
> denies everything by default and permits only outbound TLS 1.3 to IODS on one port, outbound
> syslog over TLS to the CSSP collector, and inbound HTTPS to the console from the installation
> management VLAN. The key internal interfaces are the maintenance port and the field radio. The
> maintenance port is off until a technician turns the shelter key switch, serves only the console
> on a link-local address, and has no routing to the uplink. Sensor nodes reach the gateway only
> over the paired, encrypted radio link and have no IP path to the uplink.

### Q4 {#INT-016.Q4}
Asked of: PER-ISSE · Task: S-4 · Control focus: sc-7
**A4 {#INT-016.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/test-results.md#dt-2]]
> ESG has no publicly accessible component, so part (b) has nothing to separate. The gateway
> connects to other systems only through the site switch, behind the enclave firewall that
> enforces the same permitted flows at the enclave edge. DT-2 port-scanned the uplink and the
> maintenance port: only the documented ports answered and there was no routing between ports.
> Firewall rule changes are logged and go through the configuration control board with the rest
> of the baseline.
