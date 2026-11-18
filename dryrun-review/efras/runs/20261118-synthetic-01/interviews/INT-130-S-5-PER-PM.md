---
interview_id: INT-130
run_id: 20261118-synthetic-01
task: S-5
persona: PER-PM
date: 2026-11-18
topics: [frequency criteria, minimum frequency review, metrics, lifecycle management, posture reporting]
---
# INT-130 — S-5 — PER-PM

### Q1 {#INT-130.Q1}
Asked of: PER-PM · Task: S-5 · Control focus: ca-7
On what criteria did you set the frequencies the Component does not set, with whom, and do the Component minimums suffice for EFRAS?
**A1 {#INT-130.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-129.A1]] [[ART-ORG-CONTEXT]] [[product/conops.md#limitations]]
> With the ISSM and the AODR, on 2026-11-18, I set four criteria: known weaknesses (a family
> with a partial control is watched at least quarterly until fixed), volatility (a family that
> changes with each release is watched monthly), impact level (the confidentiality of CUI and
> PII sets monthly for system and communications protection), and inheritance (controls a
> provider implements whole are watched through its monthly deliverables and reviewed
> annually). The privacy office added a fifth for the privacy family: quarterly, per its
> guidance. I reviewed the Component minimums the same day: they suffice for EFRAS; we go
> faster than them only where the list above says.

### Q2 {#INT-130.Q2}
Asked of: PER-PM · Task: S-5 · Control focus: ca-7, pm-6
Which metrics will you watch, who receives them, and how is the posture reported?
**A2 {#INT-130.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-129.A2]] [[INT-126.A1]] [[ART-ORG-CONTEXT]]
> Monthly to me, the ISSM and the AODR: mean time to remediate high and critical
> vulnerabilities (target under 30 days); highs past their remediation date (target zero); STIG
> compliance of nodes and database (target 95%, today 94% and 88%); unauthorized drift events
> not reverted within one working day (target zero); account review done on time (quarterly);
> POA&M items past due (target zero). The privacy office receives the privacy metric. A breach
> of a threshold is raised by the ISSM at the next board meeting and, if it is a high finding,
> with the AODR within a week. A quarterly posture report goes to the AO through the AODR,
> with the C-SCRM summary, as the Component program asks.

### Q3 {#INT-130.Q3}
Asked of: PER-PM · Task: S-5 · Control focus: sa-11, si-2 (software pathway)
How does the program manage software risk through the life cycle, and when does a fix leave the release cycle?
**A3 {#INT-130.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#program]] [[product/architecture.md#updates]] [[INT-128.A1]]
> Our risk-based approach covers software vulnerabilities, the supply chain, the development
> environment (the factory) and intelligence threats from the CSSP and the Component. The
> backlog captures issues, errors, threats, defects and supplier updates from development and
> operations, each prioritized at sprint planning. A fix for a critical vulnerability, or a
> high one that is exploited or reachable from the access point, goes out as an emergency
> patch within 48 hours, outside the three-week release cycle.
