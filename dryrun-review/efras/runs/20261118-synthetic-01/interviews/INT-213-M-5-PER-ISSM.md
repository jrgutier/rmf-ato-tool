---
interview_id: INT-213
run_id: 20261118-synthetic-01
task: M-5
persona: PER-ISSM
date: 2027-02-01
topics: [deliveries, scorecard, status sharing, DODIN awareness, supply chain summary]
---
# INT-213 — M-5 — PER-ISSM

### Q1 {#INT-213.Q1}
Asked of: PER-ISSM · Task: M-5 · Control focus: ca-7
How is the status shared, and what reaches the DoD Cybersecurity Scorecard?
**A1 {#INT-213.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-212.A1]] [[ART-CONMON]] [[ART-POAM]]
> The POA&M and the control status are kept in eMASS, so the Component above us and the peer
> programs on the risk board see the same data through the automated views, and it is visible,
> accessible, understandable, trusted and interoperable in the form eMASS gives it. I submit the
> system's scorecard figures with the report today. One item changes status for the vulnerability
> roll-up: POAM-020 is risk-accepted since the decision. Nothing completed.

### Q2 {#INT-213.Q2}
Asked of: PER-ISSM · Task: M-5 · Control focus: si-4, au-6
For DODIN operations, which of the areas does the monitoring strategy actually give awareness of: threats, traffic, faults, performance, bandwidth, routes, network management and employee use?
**A2 {#INT-213.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-118.A2]] [[INT-121.A2]] [[INT-207.A1]] [[ART-CONMON]]
> Three of them. Threats, through the CSSP's alerts and its log monitoring. Traffic, because the
> CSSP correlates the access point's traffic logs with our edge and web application firewall
> logs. Employee use, through user activity monitoring, which stays in DoD hands with the
> Component insider threat program. Faults, performance, bandwidth, routes and network management
> of the DODIN path are the access point operator's and the provider's; our strategy has no
> measure or record for them, and the access point's own reporting did not even reach us this
> cycle (SRV-06). I will not claim them; that is a gap for the strategy, and I raise it with the
> CISO for the organization's monitoring strategy.

### Q3 {#INT-213.Q3}
Asked of: PER-ISSM · Task: M-5 · Control focus: sr-6
What goes into the quarterly supply chain summary the plan asks for?
**A3 {#INT-213.A3}** respondent: simulated · tag: SIMULATED · basis: [[INT-208.A3]] [[INT-206.A3]] [[product/monitoring/cycle-2026-11.md#vuln-scan]]
> Supplier monitoring: the factory's hardened base image is about three months late and holds the
> report container fix (SRV-08 degraded); the CSSP's monthly external scan report did not reach us
> (SRV-03 degraded); the provider patched its control plane on time. Open supply chain findings:
> the efras-report highs that wait on the factory (POAM-002, POAM-003, POAM-017). SBOM
> vulnerability counts from the factory's rescan of 2026-11-14: two highs in efras-report and one
> medium in efras-api. No urgent condition, so no urgent notice.
