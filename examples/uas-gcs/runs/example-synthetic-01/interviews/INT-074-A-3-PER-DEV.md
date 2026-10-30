---
interview_id: INT-074
run_id: example-synthetic-01
task: A-3
persona: PER-DEV
date: 2026-10-29
topics: [ca cm assessment evidence, change process, allow-list, signed updates, SRG hardening]
---
# INT-074 — A-3 — PER-DEV

### Q1 {#INT-074.Q1}
Asked of: PER-DEV · Task: A-3 · Control focus: cm-3, cm-3.2, cm-3.4, cm-3.6, cm-3.7, cm-4, cm-4.1, cm-4.2
Show the change records for the 2.3.0 bundle.

**A1 {#INT-074.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#configuration]] [[product/architecture.md#updates]]
> Every 2.3.0 change has a CCB request with a security and privacy impact analysis signed off
> by the ISSM, who sat on the board; the certificate renewal on the workstation went through
> the same process. Each change was tested on the pre-production stations, and the control
> regression tests were re-run on the full bundle before release. The board's delivery review
> checked the bundle contents against the approved requests.

### Q2 {#INT-074.Q2}
Asked of: PER-DEV · Task: A-3 · Control focus: cm-5.6, cm-7, cm-7.1, cm-7.2, cm-7.3, cm-7.5, cm-7.8, cm-7.9, cm-10, cm-10.1, cm-11, cm-11.2, cm-14
How are least functionality, the allow-list and signed updates enforced?

**A2 {#INT-074.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/architecture.md#updates]] [[product/test-results.md#dt-1]]
> The workstation runs only signed executables on the allow-list; an unsigned test program
> was blocked, and a standard user could not install software or write to program folders.
> The ports and services register is in the design, and the quarterly review minutes for
> 2.3.0 are on file. The DT-1 port scan found only documented ports. The workstation installer
> and the GDT both reject an image with a broken signature. The program's license list covers
> every workstation product, and each open-source library has a CCB approval.

### Q3 {#INT-074.Q3}
Asked of: PER-DEV · Task: A-3 · Control focus: cm-6, cm-9
What is the state of the application SRG hardening and of the full configuration management plan?

**A3 {#INT-074.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/test-results.md#stig-scan]]
> The workstation and router settings match the STIGs with the recorded deviations, per the
> 2026-09-15 scan. For the planner I hand-recorded the settings against the SRG, but nobody
> has checked them, and the flight control and video applications have not been checked
> against the SRG at all. There is no scan content for any of them. The full configuration
> management plan is drafted and still under ISSM review; it is not signed.

### Q4 {#INT-074.Q4}
Asked of: PER-DEV · Task: A-3 · Control focus: ca-3.6, ca-9
Show the router rules for the station segment and for the brigade side.

**A4 {#INT-074.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/test-results.md#dt-1]]
> The router admits inbound sessions only from the brigade S6 management subnet, and those need
> CAC sign-in in the admin group; nothing is accepted from the brigade intelligence system.
> The internal segment holds the workstation, the GDT management port and the router, and the
> design lists each internal connection. The DT-1 scans from the uplink and the station side
> found only documented ports.
