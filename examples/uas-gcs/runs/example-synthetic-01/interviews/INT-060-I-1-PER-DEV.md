---
interview_id: INT-060
run_id: example-synthetic-01
task: I-1
persona: PER-DEV
date: 2026-10-29
topics: [STIG scan, secure configuration, benchmark mapping, open rules]
---
# INT-060 — I-1 — PER-DEV

### Q1 {#INT-060.Q1}
Asked of: PER-DEV · Task: I-1 · Control focus: cm-6, cm-2
Which benchmarks did you configure each software item against, and which scans ran?

**A1 {#INT-060.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#stig-scan]] [[product/conops.md#limitations]]
> The workstation image 2.3.0 is built to the Windows STIG and the station router to the
> network device STIG; both were scanned on all six stations on 2026-09-15 with the SCA
> watching. The mission planner has no STIG, so we hardened it by hand against the
> Application Security and Development SRG and wrote the settings down, but no scan or
> assessment has covered that. I cannot quote the benchmark release numbers from memory;
> they are in the build records, not in the material I brought today.

### Q2 {#INT-060.Q2}
Asked of: PER-DEV · Task: I-1 · Control focus: ia-2, ac-2, ia-5
What rules did the 2026-09-15 STIG scan leave open?

**A2 {#INT-060.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#stig-scan]] [[product/test-results.md#account-review]]
> No CAT I rules were open. The one open rule we carry on both the workstation and the router
> is the shared-account rule: the local `gcsmaint` account is used by several maintainers, so
> both scans flag it as a CAT II finding. The fix is per-maintainer local accounts with offline
> CAC sign-in in release 2.4. Everything else was either a pass or one of the deviations the
> configuration control board approved.

### Q3 {#INT-060.Q3}
Asked of: PER-DEV · Task: I-1 · Control focus: cm-6, ia-5
Which deviations from the benchmarks did the configuration control board approve?

**A3 {#INT-060.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#dt-1]] [[product/conops.md#environment]]
> One: the workstation keeps cached CAC sign-in for 7 days instead of the benchmark's shorter
> cached-logon limit, because platoons operate disconnected from the brigade directory for days
> at a time. The board approved it with the 2.3.0 baseline, and DT-1 tested the 7-day case.

### Q4 {#INT-060.Q4}
Asked of: PER-DEV · Task: I-1 · Control focus: si-2, ra-5
How are the firmware, our own applications and the map data covered?

**A4 {#INT-060.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#vuln-scan]] [[product/conops.md#limitations]]
> There is no DISA STIG or SRG for the vendor's ground data terminal firmware; we track it
> through the vulnerability scan. Its management web service flaw is fixed in firmware 5.2.1,
> which is still in our regression testing for the 2026-12 bundle. Our flight and video
> applications run on the hardened image and were covered by the vulnerability scan only; we
> have not run an application STIG checklist against them. The map package is data, not code.
