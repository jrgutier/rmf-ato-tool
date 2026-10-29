---
interview_id: INT-025
run_id: agent-skeleton
task: A-3
persona: PER-DEV
date: 2026-10-29
topics: [hardening pipeline, deviation records, event generation]
---
# INT-025 — A-3 — PER-DEV

### Q1 {#INT-025.Q1}
Asked of: PER-DEV · Task: A-3 · Control focus: cm-6
**A1 {#INT-025.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#configuration]] [[INT-014.A1]]
> The pipeline builds one signed image from the OS SRG and the web server, database and
> application guidance, and writes a deviation record for every rule it does not apply. Each
> record goes to the configuration control board; the image is not released until the board
> approves the open deviations. All twelve units run the image the board approved.

### Q2 {#INT-025.Q2}
Asked of: PER-DEV · Task: A-3 · Control focus: au-2
**A2 {#INT-025.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#dt-2]] [[product/architecture.md#logging]]
> Event generation is built into the image: the audit daemon on the OS, and the collector and
> console write the agreed event types and forward them over TLS. In DT-2 we generated sign-in,
> account-change, configuration-change and update events on each of the twelve units and every
> one reached the SIEM within a minute; the test case IDs and logs are in the DT-2 report.
