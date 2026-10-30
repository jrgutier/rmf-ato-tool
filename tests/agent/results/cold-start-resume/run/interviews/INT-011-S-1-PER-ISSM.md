---
interview_id: INT-011
run_id: agent-cold-start-resume
task: S-1
persona: PER-ISSM
date: 2026-10-30
topics: [baseline selection, overlays, requirements coverage]
---
# INT-011 — S-1 — PER-ISSM

### Q1 {#INT-011.Q1}
Asked of: PER-ISSM · Task: S-1
Which baseline follows from the approved categorization, and do you confirm the resolved baseline?
**A1 {#INT-011.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-CAT]] [[INT-010.A4]]
> The approved categorization drives CNSSI 1253 per-objective selection: the Appendix D
> moderate confidentiality, moderate integrity and low availability columns, plus the NSS
> privacy control baseline. The tool resolved exactly that and restricted it to the six
> controls in the scenario subset. I confirm the resolved baseline as the starting point.

### Q2 {#INT-011.Q2}
Asked of: PER-ISSM · Task: S-1
Which overlays apply, and are there organizational additions?
**A2 {#INT-011.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-009.A2]] [[ART-ORG-CONTEXT]]
> Only the account-record privacy overlay approved at C-3. The Component adds no controls of its
> own; its standards come in as parameter values: the 30-day remediation period and the
> SRG/STIG configuration settings.

### Q3 {#INT-011.Q3}
Asked of: PER-ISSM · Task: S-1
Does any requirement fall outside the selected controls?
**A3 {#INT-011.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-REQ]] [[product/conops.md#limitations]]
> REQ-01 to REQ-06 map onto ac-2, ia-2, au-2, cm-6, sc-7 and si-2. REQ-07, protecting telemetry
> in transit and accepting only paired sensors, needs sc-8 and device authentication (ia-3),
> which the six-control subset leaves out. S-2 should record that as a known scope gap.
