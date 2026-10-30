---
interview_id: INT-051
run_id: example-synthetic-01
task: S-4
persona: PER-ISSM
date: 2026-10-29
topics: [ra family, risk assessment, vulnerability scanning, risk response, privacy assessment, threat hunting]
---
# INT-051 — S-4 — PER-ISSM

### Q1 {#INT-051.Q1}
Asked of: PER-ISSM · Task: S-4 · Control focus: ra-1, ra-2, ra-3, ra-3.1, ra-3.2, ra-3.3, ra-9
How are categorization, the system risk assessment, supply chain risk, threat input and criticality handled?

**A1 {#INT-051.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-017.A1]] [[INT-033.A4]] [[product/hw-sw-inventory.md#priority]]
> Risk assessment policy and procedures come from the Component cybersecurity program; we follow
> them. The station was categorized in C-2 and the categorization was approved in C-3; I keep it
> with the security plan and review it at every major release. The system risk assessment from
> P-14 is the working risk assessment: I update it at each software release, after each test
> event and whenever a new threat report or vulnerability changes a risk, and the program
> manager signs each update. That assessment covers the supply chain of the three commercial
> items (the workstation laptop, the mission planner and the ground data terminal firmware),
> using the integrator's supplier records and the Component's supply chain threat information.
> Threat input comes from the brigade S2's threat assessment and the Component's intelligence
> threat summaries, which are all-source products; the CSSP's alerts reach me through the
> enclave and I review them weekly while stations are connected. Criticality comes from the
> asset priority in the inventory: the flight control application, the ground data terminal
> and the air vehicle endpoint are mission-critical.

### Q2 {#INT-051.Q2}
Asked of: PER-ISSM · Task: S-4 · Control focus: ra-5, ra-5.2, ra-5.4, ra-5.5, ra-5.11
How are vulnerabilities scanned and fixed, and what is open today?

**A2 {#INT-051.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#vuln-scan]] [[product/conops.md#limitations]] [[INT-031.A4]]
> The ISSO runs a credentialed scan of every connected station at least monthly and on every
> reconnection, with the scanner's vulnerability feed updated from the enclave before each
> scan. The scanner uses a dedicated scan credential on the workstation, router and ground data
> terminal, not the shared maintenance account. The scan also reports which services and
> information each station exposes on its uplink, and the router port scan in DT-1 found only
> documented ports. The integrator's contract requires it to take vulnerability reports from
> anyone and pass them to us, and the DoD vulnerability disclosure program covers the public
> side. Fixes ship in the signed quarterly bundle. What is open: the ground data terminal
> firmware fix 5.2.1 is waiting for regression testing and goes in the 2026-12 bundle, with
> the management service reachable only from the station network until then; the mission
> planner has two medium findings in a bundled library with no vendor fix date; and the 3
> medium workstation and router findings are fixed in the 2026-10 bundle. The planner was not
> covered by the STIG scan because there is no STIG for it.

### Q3 {#INT-051.Q3}
Asked of: PER-ISSM · Task: S-4 · Control focus: ra-7, ra-8, ra-10
How are findings responded to, is there a privacy impact assessment, and who hunts for threats?

**A3 {#INT-051.A3}** respondent: simulated · tag: SIMULATED · basis: [[INT-015.A1]] [[INT-050.A1]] [[product/test-results.md#dt-1]] [[product/architecture.md#leveraged]]
> Each finding gets a response in the risk assessment today: the three disclosed limitations
> have their mitigations recorded there. The POA&M itself is not opened until the assessment;
> until then I track open items in the risk assessment. For privacy, the threshold analysis is
> with the SAOP's designee; it will decide whether a full privacy impact assessment is needed,
> and I expect that decision before plan review. Threat hunting is done by the CSSP on the
> enclave using the forwarded logs; the station sends workstation and router logs, but the
> mission planner and ground data terminal logs stay local, so the hunt cannot see them.
