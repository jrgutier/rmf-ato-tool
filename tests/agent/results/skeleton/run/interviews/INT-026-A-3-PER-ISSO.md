---
interview_id: INT-026
run_id: agent-skeleton
task: A-3
persona: PER-ISSO
date: 2026-10-29
topics: [maintenance-port sign-in evidence, firewall change records, patch status per unit]
---
# INT-026 — A-3 — PER-ISSO

### Q1 {#INT-026.Q1}
Asked of: PER-ISSO · Task: A-3 · Control focus: ia-2
**A1 {#INT-026.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#account-review]] [[product/conops.md#limitations]]
> For remote users I can show you the console's audit records for October: every administrator
> and auditor session carries the person's name from the smart-card certificate. For on-site work
> I cannot: every maintenance-port session is recorded as `fieldtech`, and I have no site-visit
> log that ties a session to a technician. That is the same gap my 2026-09-12 review referred to
> the program office, and the STIG finding STG-004 on the console is still open.

### Q2 {#INT-026.Q2}
Asked of: PER-ISSO · Task: A-3 · Control focus: sc-7
**A2 {#INT-026.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/architecture.md#configuration]]
> The host firewall rules are part of the approved baseline; the nightly configuration check
> would report any rule change as drift, and there was none in August or September 2026. The only
> rule change this year went through the configuration control board with the baseline. The
> maintenance port stays off unless the key switch is turned; the console logs each time the port
> comes up, and those events only appear on the dates of site visits.

### Q3 {#INT-026.Q3}
Asked of: PER-ISSO · Task: A-3 · Control focus: si-2
**A3 {#INT-026.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#vuln-scan]] [[INT-019.A1]]
> My monthly report to the ISSM lists the bundle level of each unit and the scan results. At the
> 2026-09-30 scan ten units ran the 2026-09 bundle with no findings; esg-north-01 and esg-ridge-01
> ran the 2026-07 bundle, 63 days old, with 4 high and 9 medium vulnerabilities fixed in later
> bundles. Both units wait for their quarterly site visit, so they will stay past the 30-day period
> until then. I reported both to the program office; I have no POA&M item for them yet.
