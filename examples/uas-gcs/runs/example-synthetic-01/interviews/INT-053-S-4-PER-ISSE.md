---
interview_id: INT-053
run_id: example-synthetic-01
task: S-4
persona: PER-ISSE
date: 2026-10-29
topics: [sc family, boundary protection, denial of service, cryptography, sessions, name resolution, workstation protections]
---
# INT-053 — S-4 — PER-ISSE

### Q1 {#INT-053.Q1}
Asked of: PER-ISSE · Task: S-4 · Control focus: sc-1, sc-5, sc-5.1, sc-5.2, sc-5.3, sc-7, sc-7.3, sc-7.4, sc-7.5, sc-7.7, sc-7.8, sc-7.9, sc-7.10, sc-7.11, sc-7.12, sc-7.13, sc-7.14, sc-7.25, sc-7.28, sc-7.29, sc-20, sc-21, sc-22, sc-45, sc-45.1, sc-47
How is the station boundary protected, how are denial-of-service and name resolution handled, and where does time come from?

**A1 {#INT-053.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/architecture.md#boundary]] [[product/architecture.md#leveraged]] [[product/conops.md#limitations]] [[product/test-results.md#dt-1]]
> Communications protection policy is the Component's. The router's uplink port is the only
> external access point and the boundary edge; behind it the enclave firewall and intrusion
> detection protect the brigade side under the enclave's ATO. The router denies everything by
> default and permits only outbound TLS to the intelligence system's product drop, syslog over
> TLS to the enclave collector, LDAPS to the directory, and inbound remote administration from
> the S6 management subnet. There is no general web traffic, no VPN client and no connection to
> a public network; all outbound flows go point-to-point to named brigade services, so we use
> no proxy. The workstation, GDT management port and router sit on one isolated internal
> segment, and the aircraft link has no IP route to the uplink. The workstation host firewall
> repeats the router rules. The router rate-limits inbound traffic on the uplink and logs denied
> traffic. The weak spot is the ground data terminal: its management web service can be crashed
> from an adjacent network until firmware 5.2.1 is installed in the 2026-12 bundle; for now it
> listens only on the internal segment. The station hosts no name service: the router forwards
> lookups to the enclave's validating resolvers. Time comes from the enclave time source when
> connected; the workstation syncs from the router, and the router flags drift over one second
> after reconnection. If the aircraft link drops, the aircraft flies its pre-loaded lost-link
> route; there is no second radio.

### Q2 {#INT-053.Q2}
Asked of: PER-ISSE · Task: S-4 · Control focus: sc-8, sc-8.1, sc-8.2, sc-12, sc-13, sc-17, sc-23, sc-23.1, sc-23.3, sc-23.5, sc-28, sc-28.1, sc-28.3, sc-10
How are data in transit and at rest protected, how are keys and certificates managed, and how are sessions handled?

**A2 {#INT-053.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/architecture.md#components]] [[product/test-results.md#dt-1]]
> Every uplink flow uses TLS with DoD PKI certificates, through FIPS-validated modules in the
> workstation OS and router. The aircraft link is encrypted and keyed with keys the unit loads
> before each mission; the DT-1 test showed commands from an unkeyed terminal are rejected, and
> the link protects data before sending and on receipt. The ISSO manages the link keys and the
> workstation and router certificates, which come from DoD PKI; the station trusts only DoD PKI
> certificate authorities. Sessions on the workstation and router use unique random session
> identifiers that are invalidated at sign-out, and the router ends idle admin sessions after
> 10 minutes. The workstation disk is fully encrypted with keys held in the laptop's TPM.

### Q3 {#INT-053.Q3}
Asked of: PER-ISSE · Task: S-4 · Control focus: sc-2, sc-4, sc-15, sc-16, sc-16.1, sc-16.2, sc-18, sc-18.1, sc-18.2, sc-18.3, sc-18.4, sc-38, sc-39, sc-41
What do the workstation image and the integrator's build enforce for separation, devices, mobile code and attributes?

**A3 {#INT-053.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#configuration]] [[product/architecture.md#physical]] [[product/architecture.md#identity]]
> The STIG image separates administration from operator functions: admin tools run only for the
> admin role, and the OS isolates processes and clears shared memory between users. The laptop's
> camera and microphone are disabled in the image. Mission products carry their release marking
> as a metadata attribute, checked by the video application on export, and the export package
> is signed so the marking cannot be changed in transit. Mobile code is blocked by the STIG
> settings except the integrator-signed application components, and the integrator's build
> admits only signed code. USB storage is blocked except for the maintainer role installing
> signed bundles, and unused ports are disabled. OPSEC is the platoon's: stations stay under its
> control and transport cases lock with tamper seals.
