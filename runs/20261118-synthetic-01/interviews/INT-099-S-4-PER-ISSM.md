---
interview_id: INT-099
run_id: 20261118-synthetic-01
task: S-4
persona: PER-ISSM
date: 2026-11-18
topics: [incident handling inside the boundary, incident reporting by personnel, the incident response plan]
---
# INT-099 — S-4 — PER-ISSM

### Q1 {#INT-099.Q1}
Asked of: PER-ISSM · Task: S-4 · Control focus: ir-4
What does the program itself do when the CSSP declares an incident, and what is not in place yet?
**A1 {#INT-099.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/architecture.md#configuration]] [[product/architecture.md#updates]] [[product/conops.md#limitations]] [[product/test-results.md#dt-2]] [[INT-098.A1]]
> The ERST on-call engineer contains inside the cloud account: isolates a workload with a
> network policy, revokes a workload identity or console role, and blocks a source at the WAF.
> Eradication and recovery go through the pipeline: we redeploy from signed images and
> version-controlled templates, and restore the database to a point in time (restore tested
> once, 3 h 10 min in DT-2). The ISSO leads for the program and keeps the ticket. What is not in
> place: there is no written incident response plan yet, so nothing yet ties our steps to the
> contingency plan, which is itself only a draft, and there is no lessons-learned step that
> feeds procedures, training and tests. We have had no incident and no exercise. The incident
> response plan is written in this task, and its first tabletop runs with the contingency
> tabletop in 2027-02.

### Q2 {#INT-099.Q2}
Asked of: PER-ISSM · Task: S-4 · Control focus: ir-6
What must EFRAS personnel do when they suspect an incident?
**A2 {#INT-099.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-098.A2]] [[product/conops.md#users]]
> Every user, administrator and ERST engineer reports a suspected incident to the CSSP
> operations center and the EFRAS ISSO within one hour of discovery; the contact is on the
> sign-in banner page and in the runbook. The ISSO informs the AODR, and the Component privacy
> office within one hour for a suspected PII breach. The CSSP reports onward to the DoD central
> point of contact. Annual awareness training covers it.

### Q3 {#INT-099.Q3}
Asked of: PER-ISSM · Task: S-4 · Control focus: ir-8
What will the incident response plan contain, who approves and reviews it, and who gets it?
**A3 {#INT-099.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/stakeholders.md#roles]] [[product/conops.md#limitations]] [[INT-098.A1]]
> I write it in this task, from the template, with the CSSP. It names the ISSO as the program's
> incident lead, the ERST on-call engineers for containment and recovery and the CSSP for
> detection and analysis; it defines reportable incidents, the hand-off to the CSSP, the PII
> breach path, the link to the contingency plan, metrics (time to report, time to contain) and
> the resources the program funds. The product manager approves it, with my review, by
> 2026-12-15, and the Component CISO's office concurs. I review it annually and after every
> incident or exercise, and send it and every change to the ISSO, the ERST on-call engineers,
> the CSSP and the Component privacy office. It sits in the program document repository with
> access limited to those holders.
