---
interview_id: INT-054
run_id: example-synthetic-01
task: S-4
persona: PER-ISSO
date: 2026-10-29
topics: [si family, flaw remediation, malicious code, system monitoring, security alerts]
---
# INT-054 — S-4 — PER-ISSO

### Q1 {#INT-054.Q1}
Asked of: PER-ISSO · Task: S-4 · Control focus: si-1, si-2, si-2.2, si-2.3, si-2.4, si-2.6, si-5
How are flaws remediated on each component, how is remediation tracked, and how do security alerts reach the station?

**A1 {#INT-054.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#updates]] [[product/architecture.md#configuration]] [[product/test-results.md#vuln-scan]] [[product/conops.md#limitations]]
> System and information integrity policy and procedures are the Component's; I apply them to
> the stations. Fixes reach every component through the integrator's signed quarterly bundle,
> installed by maintainers from removable media; the installer replaces the old packages and
> firmware and removes the superseded versions. The start-up compliance check reports the
> installed bundle level to the local log, which is how I track which stations are current,
> and I record the time from a vendor fix to installation. Two gaps are open: the GDT firmware
> fix 5.2.1 is waiting for regression testing and goes in the 2026-12 bundle, and the mission
> planner has two medium library findings with no vendor fix date. Security alerts and IAVM
> notices come to me from the Component CSSP; I assess them for the station and ask the
> integrator for an out-of-cycle bundle when one applies.

### Q2 {#INT-054.Q2}
Asked of: PER-ISSO · Task: S-4 · Control focus: si-3, si-3.10, si-4, si-4.1, si-4.2, si-4.4, si-4.5, si-4.10, si-4.11, si-4.12, si-4.16, si-4.19, si-4.20, si-4.22, si-4.23, si-4.24
How is malicious code handled, and how are the station and its connections monitored?

**A2 {#INT-054.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]] [[product/architecture.md#network]] [[product/architecture.md#leveraged]] [[product/test-results.md#dt-1]]
> The workstation image runs the operating system's built-in malicious code protection in
> real time and scans removable media on insertion; signatures update with each bundle and from
> the enclave when connected. A detection quarantines the file, alerts the signed-in user and
> logs the event; suspect samples go to the CSSP for analysis. Monitoring is shared: the enclave
> runs the intrusion detection and the central log collector under its ATO, and the S6 reviews
> the collector. The station's part is the workstation and router logs: the router logs denied
> and inbound traffic on the uplink and flags any unexpected service, the workstation logs
> privileged-user activity and device connections, and drift or malware events raise a local
> alert that I review. Outbound flows go only to named brigade services, and the enclave
> sensors inspect them where they terminate. The gap is coverage: the mission planner and the
> GDT keep only local logs that are not forwarded, so the enclave cannot correlate them; DT-1
> confirmed it.

### Q3 {#INT-054.Q3}
Asked of: PER-ISSO · Task: S-4 · Control focus: si-4.14, si-4.15, si-8, si-8.2
What watches the aircraft radio link, and does the station handle e-mail or messaging?

**A3 {#INT-054.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/test-results.md#dt-1]] [[product/architecture.md#logging]]
> The GDT rejects commands from unkeyed terminals and records the attempts in its local log,
> which is not forwarded; nothing else watches the radio link. The aircraft link has no IP
> route to the uplink, so nothing from it can reach the wired network. The station has no
> e-mail, chat or messaging service at all; operators use those on other brigade systems.
