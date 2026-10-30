---
interview_id: INT-057
run_id: example-synthetic-01
task: S-5
persona: PER-ISSM
date: 2026-10-29
topics: [continuous monitoring strategy, monitoring frequencies, ongoing authorization triggers, reporting]
---
# INT-057 — S-5 — PER-ISSM

### Q1 {#INT-057.Q1}
Asked of: PER-ISSM · Task: S-5 · Control focus: ca-7, ra-5, cm-6, au-6, pm-31
How will the station apply the organizational monitoring frequencies to each control family, given long disconnected periods?

**A1 {#INT-057.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[ART-SSP]] [[product/architecture.md#configuration]]
> We keep the organization's rule: frequency follows volatility. The start-up and pre-upload
> compliance check runs continuously in the sense that it runs before every mission, so
> configuration and integrity are watched every time a station is used. Vulnerability and
> STIG scans run monthly when connected and on every reconnection. The ISSO's weekly station
> log review covers audit, and the enclave reviews forwarded logs daily. Accounts are reviewed
> quarterly. Every other family is assessed annually, one third of the controls each year, so
> all are assessed within the authorization period. Plans (contingency, incident response,
> configuration management) are reviewed annually and after each exercise or incident.

### Q2 {#INT-057.Q2}
Asked of: PER-ISSM · Task: S-5 · Control focus: ca-7, ca-7.4, ca-6
What triggers a review of the authorization, and on what time basis?

**A2 {#INT-057.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[ART-RA]]
> Time-driven: every 365 days the AO reviews the posture and the year's assessments, which
> gives three reviews within the three-year authorization period. Event-driven: a significant
> change to the boundary, components or bundle content; a new critical vulnerability with no
> mitigation; a missed remediation date on a high-risk POA&M item; a confirmed incident on a
> station; a captured or lost kit; and a change in the threat picture that raises TE-1, TE-3,
> TE-5 or TE-6 to high. The weak spots we watch closest are the shared maintenance account,
> the GDT firmware fix and the logs that are not forwarded.

### Q3 {#INT-057.Q3}
Asked of: PER-ISSM · Task: S-5 · Control focus: ca-7, pm-31, si-4
Who receives posture reports, and what metrics do they carry? What gaps limit the strategy today?

**A3 {#INT-057.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[ART-SSP]] [[product/test-results.md#dt-1]] [[product/conops.md#limitations]]
> I report quarterly to the AO, with the AODR and the Component CISO copied, and twice a year
> to the risk executive. The report carries the organization's metrics: past-due POA&M items,
> critical and high vulnerabilities older than the remediation period, STIG compliance, and
> days since each station's logs last reached the enclave collector. Two honest gaps: mission
> planner and GDT logs are local only, so the ISSO checks them by hand in the weekly review
> until forwarding is engineered; and the weekly review has so far run only at test events.
> Monitoring of those components is manual until then, and we do not claim near-real-time
> monitoring for them. The ISSO collects station data; the SCA does the annual assessments.
