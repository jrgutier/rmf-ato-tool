---
interview_id: INT-098
run_id: 20261118-synthetic-01
task: S-4
persona: PER-CSSP
date: 2026-11-18
topics: [incident handling support, incident reporting path and timeline]
---
# INT-098 — S-4 — PER-CSSP

### Q1 {#INT-098.Q1}
Asked of: PER-CSSP · Task: S-4 · Control focus: ir-4
Which parts of incident handling does the CSSP perform for EFRAS, and which stay with the program?
**A1 {#INT-098.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[product/conops.md#environment]] [[INT-072.A1]] [[INT-091.A1]]
> We do detection and analysis: we correlate the forwarded EFRAS logs 24x7, declare and
> categorize an incident, open a ticket to the EFRAS ISSO and ISSM, and give analysis and
> containment advice. We run the same handling playbook for every system we serve in the
> Component, so the rigor and the reports are comparable across them. We cannot touch the EFRAS
> cloud account: containment, eradication and recovery inside the boundary are the program's
> own, done by its on-call engineers. We expect the program's incident response plan to name
> those people and to say how it hands off to us; today we have only the contact list in the
> service agreement.

### Q2 {#INT-098.Q2}
Asked of: PER-CSSP · Task: S-4 · Control focus: ir-6
How and how fast must EFRAS report a suspected incident to you, and where do you report it?
**A2 {#INT-098.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[INT-072.A1]]
> The service agreement asks the program to report a suspected incident to our operations
> center by phone or ticket within one hour of discovery. We report it onward to the designated
> DoD central point of contact (DoD CERT) and to the EFRAS AO's office within the timelines of
> the DoD cyber incident handling program. A suspected breach of maintainer PII also goes from
> the program to the Component privacy office; we copy them when our analysis touches PII.
