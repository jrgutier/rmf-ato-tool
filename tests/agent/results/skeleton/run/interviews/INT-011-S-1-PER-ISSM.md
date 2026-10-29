---
interview_id: INT-011
run_id: agent-skeleton
task: S-1
persona: PER-ISSM
date: 2026-10-29
topics: [baseline selection, overlays, organizational additions, uncovered requirements]
---
# INT-011 — S-1 — PER-ISSM

### Q1 {#INT-011.Q1}
Asked of: PER-ISSM · Task: S-1
**A1 {#INT-011.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-CAT]] [[INT-010.A4]]
> Yes. The categorization the AODR approved is moderate, moderate, low, and the tool resolved
> the SP 800-53B moderate baseline at its high-water mark, restricted to the six controls this
> run's scope names. I confirm SP800-53B-MODERATE-SUBSET-6 as the baseline ID. It is not a
> CNSSI 1253 per-objective selection; that step is still to come, so I do not call it one.

### Q2 {#INT-011.Q2}
Asked of: PER-ISSM · Task: S-1
**A2 {#INT-011.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-CAT]] [[INT-009.A1]] [[INT-009.A2]] [[ASM-002]]
> No overlay applies. CNSSI 1253 Attachment 5 (classified) and Attachment 2 (space) are out for
> the reasons in ART-CAT. Attachment 6 (privacy) is out only under ASM-002; if the privacy office
> finds PII, the AODR's condition sends the categorization back and I re-run selection with the
> privacy overlay before the baseline is final.

### Q3 {#INT-011.Q3}
Asked of: PER-ISSM · Task: S-1
**A3 {#INT-011.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[product/architecture.md#updates]] [[product/architecture.md#configuration]]
> Organizational additions come in as parameter values, not extra controls: the 30-day flaw
> remediation period and configuration to the applicable DISA SRGs and STIGs. Those are already
> in the seeded tailoring file as parameter actions on si-2 and cm-6, with the quarterly account
> review on ac-2 and the annual event-list review on au-2.

### Q4 {#INT-011.Q4}
Asked of: PER-ISSM · Task: S-1
**A4 {#INT-011.A4}** respondent: simulated · tag: SIMULATED · basis: [[ART-REQ]] [[product/conops.md#limitations]]
> Against the requirements: REQ-07, telemetry protected in transit and accepted only from paired
> sensor nodes, has no control in this six-control subset; sc-8 and the device identification
> controls would carry it. Flag it for S-2. REQ-01 and REQ-06 are covered by ac-2 and si-2 but
> are known gaps today: the shared fieldtech account and updates only at quarterly visits.
