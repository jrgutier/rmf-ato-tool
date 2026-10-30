---
interview_id: INT-021
run_id: agent-cold-start-resume
task: A-3
persona: PER-DEV
date: 2026-10-30
topics: [identity federation evidence, host firewall evidence, update bundle and patch latency evidence]
---
# INT-021 — A-3 — PER-DEV

### Q1 {#INT-021.Q1}
Asked of: PER-DEV · Task: A-3 · Control focus: ia-2
Show the evidence that console users are uniquely identified, and explain the open STIG finding STG-004.
**A1 {#INT-021.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#dt-2]] [[product/architecture.md#identity]] [[product/conops.md#limitations]]
> In DT-2 every `admin` and `auditor` sign-in went through the installation identity service with
> a DoD PKI smart card, the console session carried the person's identity from the group claim,
> and users without an approved claim were refused. Lockout after 5 failures and the 15-minute
> session lock also passed. STG-004 is real: on the maintenance port the 10 field technicians
> all sign in as the shared local account `fieldtech`, so those sessions are not tied to a
> person. Per-technician accounts with smart-card login are in release 2.3, planned for 2027-03;
> nothing has changed on the fielded units yet.

### Q2 {#INT-021.Q2}
Asked of: PER-DEV · Task: A-3 · Control focus: sc-7
How is the host firewall rule set enforced, and what did the port scans show?
**A2 {#INT-021.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/test-results.md#dt-2]] [[product/test-results.md#config-scan]]
> The rule set is part of the signed OS image: deny by default, with outbound TLS 1.3 to IODS,
> syslog over TLS to the CSSP, and inbound HTTPS from the management VLAN only. The maintenance
> port stays down until the shelter key switch enables it and has no route to the uplink. In
> DT-2 the port scans from the installation network and from the maintenance port found only
> the documented ports and no routing between them, and the witnessed 2026-09-30 scan found the
> approved image, firewall settings included, on all 12 units.

### Q3 {#INT-021.Q3}
Asked of: PER-DEV · Task: A-3 · Control focus: si-2
What is in the update bundle process, and what was the patch status per unit at the last scan?
**A3 {#INT-021.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#updates]] [[product/test-results.md#vuln-scan]] [[product/conops.md#limitations]]
> We publish a signed monthly bundle covering the OS, collector, console and database, test it
> on our reference units, and the CCB approves it as a baseline change; units check the
> signature before install. Fielded units only get the bundle at the quarterly site visit. At
> the 2026-09-30 scan 10 of 12 units ran the 2026-09 bundle with no vulnerabilities; esg-north-01
> and esg-ridge-01 still ran the 2026-07 bundle, 63 days old, with 4 high and 9 medium
> vulnerabilities fixed in later bundles. Remote update over the uplink is release 2.2, planned
> for 2026-12.
