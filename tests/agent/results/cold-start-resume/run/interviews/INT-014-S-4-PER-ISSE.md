---
interview_id: INT-014
run_id: agent-cold-start-resume
task: S-4
persona: PER-ISSE
date: 2026-10-30
topics: [configuration settings, deviations, drift monitoring]
---
# INT-014 — S-4 — PER-ISSE

### Q1 {#INT-014.Q1}
Asked of: PER-ISSE · Task: S-4 · Control focus: cm-6
How are configuration settings established, implemented and kept under control?
**A1 {#INT-014.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#configuration]] [[product/test-results.md#config-scan]] [[ART-STIG]]
> The developer builds one signed OS image from the General Purpose OS SRG and the applicable
> application and web server guidance; the pipeline applies the settings to the OS, collector,
> console and database and records each deviation, which the configuration control board
> approves and the STIG summary lists. A nightly check on every unit reports drift to the
> SIEM, and baseline changes go through the CCB. The 2026-09-30 scan found the baseline on all
> 12 units with only the approved deviations.
