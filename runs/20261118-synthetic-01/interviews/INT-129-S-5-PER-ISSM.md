---
interview_id: INT-129
run_id: 20261118-synthetic-01
task: S-5
persona: PER-ISSM
date: 2026-11-18
topics: [monitoring frequencies per family, automated tools, data architecture, event triggers, vulnerability management]
---
# INT-129 — S-5 — PER-ISSM

### Q1 {#INT-129.Q1}
Asked of: PER-ISSM · Task: S-5 · Control focus: ca-7 (all families)
How often will each control family be monitored, by what method and by whom, given the Component minimums?
**A1 {#INT-129.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[INT-123.A1]] [[product/architecture.md#logging]] [[product/architecture.md#configuration]]
> We take the Component minimums as they are where they exist: vulnerability scanning weekly
> (ra), configuration baseline checks monthly (cm), audit log review weekly (au), account
> reviews quarterly (ac), flaw remediation status monthly (si), the incident response and
> contingency plan tests annually (ir, cp), and an assessment of at least a third of the
> controls each year (ca). Some controls go faster: the CSSP correlates au-6 and si-4
> continuously, the drift scan checks cm-2 daily (it runs hourly), the POA&M and the strategy
> itself (ca-5, ca-7) are reviewed monthly, and cp-9 backups are checked monthly. For the
> other families we set our own: identification and authentication quarterly (two partial
> controls), maintenance and personnel security quarterly (maintenance sessions and leavers),
> system and communications protection monthly (boundary and crypto settings change with
> releases), acquisition and supply chain monthly (a release every three weeks), PII processing
> quarterly as the privacy office asked, and awareness, planning, program management, physical
> and media protection annually; the last two are inherited and watched through the provider's
> monthly deliverables.

### Q2 {#INT-129.Q2}
Asked of: PER-ISSM · Task: S-5 · Control focus: ca-7, ra-5, si-2, cm-6
Which automated tools assess which controls, how often, and how are their results handled?
**A2 {#INT-129.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-123.A1]] [[INT-108.A1]] [[INT-114.A1]] [[INT-118.A2]] [[product/test-results.md#stig-scan]]
> Six tools. The Component's SCAP STIG scanner on the nodes and database, monthly and at each
> release (cm-6). The hourly drift scan against the templates (cm-2, cm-3). The Component's
> authenticated vulnerability scanner inside the account, weekly (ra-5, si-2). The software
> factory's image and dependency scanners, at every build and daily against the SBOMs (ra-5,
> sa-11, sr-3, sr-11). The CSSP's SIEM on the forwarded logs, continuous (au-6, si-4). The CSSP's
> non-authenticated external scan through the access point, monthly (ra-5). Each one's results
> go to the ISSO; the ISSO triages within two working days, opens an issue for each finding,
> and the monthly report to the ISSM and the AODR summarizes them. Tools were chosen because
> they are the Component's or the factory's approved tools and cover our components; the ISSE
> checks each one's coverage against the inventory at each release and updates the scan
> profiles and allow-lists. Data flows: the scanners and the drift scan write to CMP-LOGS and the
> Component continuous monitoring dashboard; the CSSP keeps its own SIEM; the ISSO pulls a
> monthly roll-up from the dashboard for the posture report. Manual monitoring stays for
> account reviews, plan reviews, provider deliverables, privacy reviews and the sandbox and
> WAF settings, because no tool reaches them. False positives go through the allow-list or an
> ISSO-approved justification; the CSSP tunes its use cases quarterly and after each incident.

### Q3 {#INT-129.Q3}
Asked of: PER-ISSM · Task: S-5 · Control focus: ca-7, ra-3
Which events trigger an assessment or a new authorization, and how is the boundary revisited?
**A3 {#INT-129.A3}** respondent: simulated · tag: SIMULATED · basis: [[INT-122.A1]] [[INT-107.A1]] [[ART-ORG-CONTEXT]]
> A confirmed incident involving PII or a privileged identity triggers an assessment of the
> controls involved. A significant change (the board's criteria: new interconnection, new data
> type, boundary or identity change, privacy safeguards) triggers an assessment, and the AO
> decides whether to reauthorize. New threat information that the CSSP or the Component rates
> high for our components triggers an assessment. A change of mission or of the information
> types triggers reauthorization. A risk assessment update that raises residual risk above the
> Component tolerance triggers both. The ISSE and I revisit the boundary every quarter against
> the account and the inventory. The authorization is reviewed at least every three years.
> We designate the system GENSER for DODIN reporting.
