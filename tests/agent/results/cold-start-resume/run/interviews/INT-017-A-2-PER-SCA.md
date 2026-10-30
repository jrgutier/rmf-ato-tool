---
interview_id: INT-017
run_id: agent-cold-start-resume
task: A-2
persona: PER-SCA
date: 2026-10-30
topics: [assessment scope, methods, reuse of test results, team independence, schedule, rules of engagement]
---
# INT-017 — A-2 — PER-SCA

### Q1 {#INT-017.Q1}
Asked of: PER-SCA · Task: A-2 · Control focus: all
What is in scope, and which methods will you apply to each control?
**A1 {#INT-017.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-SSP]] [[ART-BASELINE]]
> The whole tailored baseline is in scope, all six controls, with no exclusions. Every control
> gets examine (the SSP statement, configuration and records) and interview (the ISSO, ISSE or
> developer who owns it). We add test where the control is technical: ac-2 and ia-2 sign-in and
> lockout, au-2 event delivery to the SIEM, cm-6 the configuration scan, sc-7 a port scan, and
> si-2 the vulnerability scan. Depth is focused and coverage covers all twelve units for the
> scans; for the shared providers we assess only the ESG side and rely on their authorizations.

### Q2 {#INT-017.Q2}
Asked of: PER-SCA · Task: A-2 · Control focus: all
Which developer or developmental test results will you reuse?
**A2 {#INT-017.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#dt-2]] [[product/test-results.md#config-scan]] [[product/test-results.md#vuln-scan]] [[product/test-results.md#account-review]]
> We reuse DT-2 (sign-in, lockout, session lock, audit delivery, port scan) because it ran on the
> production configuration and we hold the raw logs. The 2026-09-30 configuration scan was
> assessor-witnessed, so we reuse it for cm-6. We reuse the 2026-09-30 vulnerability scan and
> the 2026-09-12 account review record as evidence, and we rerun the vulnerability scan on all
> units during the assessment to see the current patch state.

### Q3 {#INT-017.Q3}
Asked of: PER-SCA · Task: A-2 · Control focus: all
Who is on the team, and how independent are they?
**A3 {#INT-017.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-SSP]]
> I lead the assessment from the SCA organization, which reports outside the program office, so
> the team is independent of the program. A second assessor from the same office runs the scans.

### Q4 {#INT-017.Q4}
Asked of: PER-SCA · Task: A-2 · Control focus: all
What is the schedule and what are the rules of engagement?
**A4 {#INT-017.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#top]]
> Kickoff 2026-11-02, interviews 2026-11-03 to 2026-11-05, scans 2026-11-09 to 2026-11-11,
> out-brief 2026-11-20. Scans run only on the pre-production units at the test sites, in a
> window agreed with the ISSO, who is notified 48 hours ahead and can stop any test; no testing
> on installation networks or provider systems, and no change to unit configuration.
