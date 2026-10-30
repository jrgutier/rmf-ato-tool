---
interview_id: INT-045
run_id: example-synthetic-01
task: S-4
persona: PER-ISSO
date: 2026-10-29
topics: [ir family, ma family, incident response, CSSP reporting, maintenance, remote administration]
---
# INT-045 — S-4 — PER-ISSO

### Q1 {#INT-045.Q1}
Asked of: PER-ISSO · Task: S-4 · Control focus: ir-1, ir-2, ir-2.3, ir-3, ir-3.2, ir-8, ir-8.1, ir-9, ir-9.2, ir-9.3, ir-9.4
What does the incident response plan cover today, and how is it trained and tested?

**A1 {#INT-045.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[product/conops.md#availability]] [[ART-ORG-CONTEXT]]
> Policy and the spillage procedure come from the Component cybersecurity program. The
> station incident response plan is started in S-4 as ART-IRP and today is only a summary:
> the operator or maintainer tells the ISSO, the ISSO reports to the enclave's CSSP, and the
> platoon isolates the station by pulling the uplink and swaps in a spare kit. The full plan,
> including breach handling for the user names in account and audit records, role-based
> incident and spillage training, and the first tabletop test coordinated with the brigade
> are planned before fielding. For a spill the ISSO calls the brigade security manager, the
> station is reimaged from the signed bundle, the spare station keeps the mission going, and
> the security manager handles anyone exposed to the information.

### Q2 {#INT-045.Q2}
Asked of: PER-ISSO · Task: S-4 · Control focus: ir-4, ir-4.1, ir-4.3, ir-4.4, ir-4.6, ir-4.7, ir-4.8, ir-4.12, ir-4.13, ir-4.14, ir-5, ir-5.1, ir-6, ir-6.1, ir-6.2, ir-6.3, ir-7, ir-7.1, ir-7.2
How are incidents detected, handled, tracked and reported, and what does the enclave provide?

**A2 {#INT-045.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[product/architecture.md#logging]] [[product/test-results.md#dt-1]] [[product/conops.md#limitations]]
> The Brigade Tactical Network Enclave's CSSP runs the security operations center, intrusion
> detection, malware and forensic analysis, the incident ticket system and the reporting portal
> under its own ATO. The station's part: the ISSO reports suspected incidents to the CSSP
> through the portal within one hour, the CSSP ticket tracks each one to closure, and the ISSO
> preserves a disk image before a reimage. The CSSP correlates station events with the rest of
> the brigade and with external reports. Workstation and router logs reach the enclave
> collector, but the mission planner and GDT logs are not forwarded, so the CSSP cannot see or
> correlate those components; the ISSO checks those local logs by hand during an incident. Insider concerns go to the
> brigade security manager, but maintenance actions under the shared `gcsmaint` account cannot
> be tied to a person. The ISSO also reports vulnerabilities found in an incident to the
> integrator, which passes supply-chain issues to the vendors.

### Q3 {#INT-045.Q3}
Asked of: PER-ISSO · Task: S-4 · Control focus: ma-1, ma-2, ma-3, ma-3.1, ma-3.2, ma-3.3, ma-3.4, ma-3.5, ma-3.6, ma-4, ma-4.1, ma-4.3, ma-4.4, ma-4.6, ma-4.7, ma-5, ma-6, ma-6.1
How is maintenance, local and remote, controlled and recorded?

**A3 {#INT-045.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#users]] [[product/conops.md#limitations]] [[product/architecture.md#network]] [[product/architecture.md#updates]] [[product/conops.md#availability]]
> Field maintainers replace hardware, run diagnostics and install the signed quarterly bundle,
> and record each action in the station maintenance log; the ISSO keeps the list of the
> platoon's authorized maintainers. They sign in with the shared `gcsmaint` account, so the
> log and the audit trail show the account, not the person. The diagnostic kit and its tools
> are part of the baseline, are inspected at each setup with the case seals, are updated in
> the bundle, and never leave platoon control; removable media are scanned and the bundle
> signature is checked before install. Remote administration comes only from the brigade S6
> management subnet, with CAC sign-in over encrypted sessions; the router logs each session,
> the logs go to the enclave collector, the S6 reviews them, and idle sessions are dropped.
> A failed station is replaced from brigade spare stock within 4 hours.
