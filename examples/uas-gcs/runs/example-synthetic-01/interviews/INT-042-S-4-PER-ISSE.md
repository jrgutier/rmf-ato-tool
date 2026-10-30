---
interview_id: INT-042
run_id: example-synthetic-01
task: S-4
persona: PER-ISSE
date: 2026-10-29
topics: [cm family, baseline, change control, least functionality, inventory, signed components]
---
# INT-042 — S-4 — PER-ISSE

### Q1 {#INT-042.Q1}
Asked of: PER-ISSE · Task: S-4 · Control focus: cm-1, cm-2, cm-2.2, cm-2.3, cm-2.7, cm-3, cm-3.2, cm-3.4, cm-3.6, cm-3.7, cm-4, cm-4.1, cm-4.2, cm-9
How are the baseline and changes to it controlled?

**A1 {#INT-042.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#configuration]] [[product/architecture.md#updates]] [[product/test-results.md#top]]
> Policy comes from the Component cybersecurity program. The baseline for each component is the
> integrator's released configuration: the workstation image on the Windows STIG, the router on
> the network device STIG with deviations in the STIG summary, the hand-recorded planner
> settings, and the GDT and application versions. The compliance check at every start-up and
> before each mission upload compares the station to the baseline and logs drift; the integrator
> keeps the last two released baselines so a station can roll back. Stations deploy with the
> same hardened image whatever the area. Every change goes to the SUGS-PO CCB, where the ISSM
> sits as security representative, with an impact analysis; the integrator tests each change and
> the control settings on the six pre-production stations at the test range, separate from
> fielded stations, before it enters the quarterly bundle, and the CCB reviews delivered changes
> against the request. Crypto key and certificate changes on the workstation and GDT go through
> the same board. The CM plan is written in S-4 as ART-CMP.

### Q2 {#INT-042.Q2}
Asked of: PER-ISSE · Task: S-4 · Control focus: cm-5, cm-5.1, cm-5.5, cm-5.6, cm-6, cm-6.1
Who can change the configuration, and how are settings set and verified?

**A2 {#INT-042.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/conops.md#limitations]] [[product/test-results.md#stig-scan]]
> Only the `admin` role, the maintainers through `gcsmaint`, and the GDT vendor administrator
> account can change configuration; the OS enforces it and logs every change. Because
> `gcsmaint` is shared and the GDT has one vendor admin account, changes made through them cannot
> be tied to a person. System libraries and program folders are writable only by
> administrators. Workstation and router settings follow their STIGs and are checked
> automatically at start-up and by the SCA-witnessed scan; the planner has no STIG, its
> hand-recorded hardening against the Application Security and Development SRG has never been
> assessed, and the scan did not cover it.

### Q3 {#INT-042.Q3}
Asked of: PER-ISSE · Task: S-4 · Control focus: cm-7, cm-7.1, cm-7.2, cm-7.3, cm-7.5, cm-7.8, cm-7.9, cm-8, cm-8.1, cm-8.2, cm-8.3, cm-10, cm-10.1, cm-11, cm-11.2, cm-12, cm-12.1, cm-14
What runs on the station, how is it inventoried, and what can be installed?

**A3 {#INT-042.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/hw-sw-inventory.md#items]] [[product/architecture.md#updates]] [[product/architecture.md#network]] [[product/architecture.md#physical]]
> Each component runs only the functions its mission role needs, and the router allows only the
> documented ports. The workstation runs an allow-list of signed executables from the integrator
> bundle; anything else is blocked, including software users try to install, and only the
> bundle installer running as administrator installs software. Unregistered USB devices are
> blocked except platoon-controlled media. The CCB reviews functions, ports and the allow-list
> every quarter with the bundle. The inventory lists every item by CMP and INV ID; the
> integrator updates it with each bundle and at each installation or removal, and the start-up
> check reports any component or USB device not in it. Licenses, including the planner's, are
> tracked by the program office; open-source libraries are approved by the CCB. Mission data
> stays on the workstation's encrypted disk and the enclave product drop, as listed in the
> design. The station installs only the signed quarterly bundle and signed GDT firmware images,
> and checks the signature before install.
