---
artifact_id: ART-CONMON
run_id: 20261118-synthetic-01
produced_by_task: S-5
touched_by: [S-5, S-6, M-2]
sources: [INT-129.A1, INT-129.A2, INT-129.A3, INT-130.A1, INT-130.A2, INT-130.A3, INT-131.A1, INT-132.A1, ART-ORG-CONTEXT, ART-SSP, INT-208.A1, INT-208.A2]
---
# Continuous monitoring strategy

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Fleet Readiness Analytics Service | C-1 |
| Acronym | EFRAS | C-1 |
| System ID | EFRAS | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | EFRAS-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-MODERATE, CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-50 | S-1 |
| Classification and handling markings | unclassified; markings: CUI | C-1 |
| IT type | major-application, networked | C-1 |
| Owning organization | Aviation Readiness Software Program Office (ARSPO), naval aviation PEO (fictional) | C-1 |
| System version | 1.5 (MVCR) (released 2026-10-27) | C-1 |
| Operational environment | production | C-1 |
| Life-cycle phase | PH-PD | C-1 |
| National security system | no | C-1 |
| Missions and business functions | MSN-01 Naval aviation readiness: keeping aircraft mission-capable; MSN-02 Aircraft maintenance and readiness management; MSN-03 Daily readiness reporting for squadron, air wing and fleet (BP-01); MSN-04 Part failure forecasting for early part orders (BP-02); MSN-05 Fleet readiness analysis and de-identified data set export (BP-03) | P-8 |
<!-- END rmf:facts -->

## Strategy overview

This strategy applies the Component continuous monitoring strategy of ART-ORG-CONTEXT (its
procedure POL-02, its minimum frequencies and its quarterly posture reporting) to the system,
and gives the AO the data to judge the authorization between reviews: a time trigger of three
years and event triggers [[ART-ORG-CONTEXT]] [[INT-129.A1]] [[INT-129.A3]]. Compliance with the
planned responses (POA&M milestones, remediation times, plan approval dates) is tracked monthly
by the ISSM; effectiveness is shown by the tools, the yearly third of control assessments and the
metrics, watched by the ISSO; change to the system is caught by the board records, the drift scan
and the quarterly boundary review, and change to its environment by threat monitoring and
provider notices, watched by the ISSE (`monitoring` in `artifacts/data/conmon.yaml`)
[[INT-129.A2]] [[INT-129.A3]]. The supplier monitoring of the C-SCRM plan feeds the monthly
roll-up and the quarterly report [[INT-123.A4]].

## Monitoring frequencies

Every family of the baseline has a frequency in `conmon.yaml` `frequencies`, none less frequent
than the Component minimum: ra and au weekly; cm, si, sa, sc and sr monthly; ac, ia, ma, ps and
pt quarterly; at, ca, cp, ir, mp, pe, pl and pm annually. Six controls go faster than their
family: au-6 and si-4 continuously (the CSSP's SIEM), cm-2 daily (the hourly drift scan), and
ca-5, ca-7 and cp-9 monthly. One goes slower: ra-3 annually, because the Component's weekly ra
minimum is meant for vulnerability scanning (ra-5), and the risk assessment has its own update
triggers (see Risk assessment upkeep) [[INT-129.A1]] [[ART-ORG-CONTEXT]]. Methods and the responsible role are in each record:
the ISSO for access, audit, identification, maintenance, personnel, vulnerability and flaw
remediation; the ISSE for configuration, contingency, communications protection and supply
chain; the ISSM for assessment, awareness, incident response, planning, program management,
acquisition and the privacy family with the privacy office; the common control provider liaison
for the inherited physical and media controls [[INT-129.A1]] [[INT-131.A1]]. The PM reviewed the
Component minimums on 2026-11-18 and found them sufficient for the system (`minimum_review`)
[[INT-130.A1]].

## Frequency criteria

The Component strategy sets the frequencies of ac, au, ca, cm, cp, ir, ra and si
(`organizational_frequencies`). For the rest, the PM established five criteria on 2026-11-18
with the ISSM and the AODR, and with the privacy office for the privacy family: FC-01 known
weakness (ia and sa hold partial controls, so at least quarterly or monthly until fixed), FC-02
volatility (families that change with each three-week release or with staff turnover), FC-03
impact level (the moderate confidentiality of CUI and PII sets monthly for sc), FC-04 rare
change or whole inheritance (annual review on the provider's monthly deliverables for at, mp,
pe, pl and pm) and FC-05 the privacy office's reporting requirement (quarterly for pt)
[[INT-130.A1]] [[INT-131.A1]]. The AO or AODR approves the strategy and the minimum frequency
of each control with the plans at S-6 (`approval`) [[INT-126.A2]].

## Privacy continuous monitoring

The system processes maintainer PII, so `conmon.yaml` `privacy` is its privacy continuous
monitoring strategy, on the guidance of the Component privacy office (PER-PRIV): pt-2 and pt-3
quarterly while exports remain re-identifiable, ra-8 quarterly until the PIA is approved and
annually after, si-12 monthly (each purge checked), at-2 annually, and every other control the
NSS privacy baseline or the Privacy Overlay selected (37 more, listed one by one) at its
family's frequency or override in this strategy. No control was added
beyond the Component's strategy, so no added-control consultation was needed [[INT-131.A1]].
The privacy metric MET-07 goes to the privacy office quarterly [[INT-130.A2]].

## Automated tools and data

Six tools assess controls by test (`tools`): TOOL-01, the Component's SCAP STIG scanner, monthly
(cm-6); TOOL-02, the hourly drift scan, reviewed daily (cm-2, cm-3); TOOL-03, the Component's
authenticated vulnerability scanner, weekly (ra-5, si-2); TOOL-04, the software factory's image
and dependency scanners, daily (ra-5, sa-11, sr-3, sr-11); TOOL-05, the CSSP's SIEM, continuous
(au-6, si-4); TOOL-06, the CSSP's external scan, monthly (ra-5). Each one's results go to the
ISSO, who triages within two working days; each was chosen as the Component's, the factory's or
the CSSP's approved tool covering the components; the ISSE checks coverage and profiles at each
release. None follows a desired-state specification yet; the drift scan compares with the
templates without a formal desired-state record [[INT-129.A2]]. Data is collected into CMP-LOGS,
the Component dashboard and the CSSP's SIEM, analyzed by the ISSO and the CSSP, retrieved as a
monthly roll-up and delivered to the PM, the ISSM and the AODR monthly and to the AO quarterly.
Account, plan, provider, privacy, sandbox and WAF reviews stay manual because no tool reaches
them (`architecture`) [[INT-129.A2]].

## Ongoing authorization triggers

The time trigger is 1095 days: the authorization is reviewed at least every three years. Events
(`events`): EV-01 a confirmed incident involving PII or a privileged identity (assessment);
EV-02 a significant change (assessment and reauthorization); EV-03 high-rated threat information
for a component (assessment); EV-04 a change of mission or information types (reauthorization);
EV-05 a risk assessment update raising residual risk above moderate (both). The loss of the cloud
provider's provisional authorization or of the CSSP agreement also triggers a review
(`ongoing_authorization`). The ISSM and the ISSE revisit the boundary quarterly
(`boundary_review`) [[INT-129.A3]].

## Threat monitoring

The CSSP watches daily the activity of threat actors against DoD logistics and readiness data,
new protective techniques and signatures, and the threat to the cloud region and the access
point, from JFHQ-DODIN advisories, the Component threat assessment, the provider's bulletins,
its own feeds and the factory's advisories, and tells the ISSO within a working day
(`threat_monitoring`) [[INT-132.A1]]. A major change in the threat triggers EV-03 and feeds M-1's
change analysis and M-3's risk response [[INT-129.A3]].

## Metrics and reporting

Seven metrics (`metrics`), each with its objective, controls, baseline, threshold and review:
MET-01 mean time to remediate highs (30 days), MET-02 highs past due (zero), MET-03 STIG
compliance (95%; 94% and 88% today), MET-04 drift not reverted within a working day (zero),
MET-05 account reviews on time, MET-06 POA&M items past due (zero), MET-07 re-identifiable
records in sampled exports (zero after release 1.6). They go monthly or quarterly to the PM, the
ISSM and the AODR, MET-07 also to the privacy office, and M-1, M-2, M-3 and M-5 use them. A breach
goes to the next board meeting, and a high one to the AODR within a week [[INT-130.A2]]. The
posture report goes quarterly to the AO through the AODR, with the C-SCRM summary; the system is
designated GENSER for DODIN reporting (`reporting`) [[INT-130.A2]] [[INT-129.A3]].

## Risk assessment upkeep

Under the Component approach, the system risk assessment (ART-RA) is updated annually and at each
major release, a significant change, high-rated threat information, an incident involving PII or
a privileged identity, or a change in a critical supplier. An update revises the threat sources
and events, the vulnerabilities monitoring found, likelihood and impact, and the residual risk of
each open weakness, and goes to the PM, the AODR and the AO (`risk_assessment`); M-4 applies it
[[INT-129.A3]] [[ART-ORG-CONTEXT]].

## Security measurement

Two information needs (`measurement`): whether known vulnerabilities are fixed in time (high
priority) and whether configurations stay at their baseline (moderate). MSR-01 (mean days to
remediate, at most 30) and MSR-02 (STIG compliance, at least 95%) satisfy them, for the ISSM, the
AODR and the ISSE. Data is collected automatically into the dashboard, computed monthly by the
ISSO, accessible to the program, the AO's office and the Component working group, and reported
in the monthly roll-up and the quarterly report [[INT-130.A2]] [[INT-129.A2]].

## Vulnerability management

The system runs all five steps of the DoD process: identification, analysis, analysis and
reporting, remediation or mitigation, and verification and monitoring. Configuration management
(ART-CMP), the inventory (ART-INV) and the POA&M (ART-POAM, from A-6) support it. Vulnerabilities
are identified from scans run with NIST SP 800-115 as the reference, the CVE list, vendor
bulletins, directed actions, incident history, the risk assessment and assessments, and
incident reports and logs are cross-referenced with CVE, risk assessment data and vendor
bulletins; only the sandbox and WAF reviews are manual, because no scanner reaches them
[[INT-129.A2]]. The factory scanners (TOOL-04) serve every phase from development to
retirement, and the authenticated scanner and the STIG scanner serve operational test and
operations. Authenticated scans run weekly, non-authenticated monthly (TOOL-06). Managed
services and node images are patched by the provider, base images come from the DoD software
factory, and EFRAS code and dependencies are patched by the program; the weekly authenticated
scan checks the reach of patching, and an unpatched node or image is replaced through the
pipeline at the next release, or within 48 hours for a critical finding. MET-01 (mean time to
patch) and MET-02 (exposure past due) evaluate patching over time. CMP-LOGS, forwarded to the
CSSP's SIEM, is the central log repository (`vulnerability_management`) [[INT-129.A2]]
[[INT-130.A2]] [[INT-130.A3]] [[INT-132.A1]]. Under the software pathway, the risk-based
lifecycle approach covers software vulnerabilities, the supply chain, the development
environment and intelligence threats; the backlog captures issues, errors, threats, defects and
supplier updates; and a fix for a critical, or an exploited or exposed high, vulnerability ships
within 48 hours outside the release cycle (`lifecycle_approach`) [[INT-130.A3]].

## Roles and tools

The ISSO collects and triages tool results and runs the manual reviews; the ISSE keeps tool
coverage and the boundary review; the ISSM analyzes the roll-up and reports; the PM receives it
and acts; the CSSP collects and analyzes the logs and runs the external scan; the common control
provider liaison reviews the provider's deliverables. Two activities are delegated
(`delegations`): continuous log correlation, detection and the external scan to the CSSP under
SVA-001, and monitoring of the platform's physical, media and infrastructure controls to the
cloud provider (LA-01) under SVA-002 [[INT-129.A2]] [[INT-132.A1]]. Detection covers at all
times the networks (access point and edge logs), the physical environment (the provider's
monitoring under its authorization), personnel activity (application, console and break-glass
logs), external providers (cloud account activity and provider notices) and computing (cluster,
node and database logs and the drift scan) (`detection_coverage`). The CSSP tunes its use cases
quarterly and after each incident with the ISSO, and scanner false positives go through the
allow-list or an approved justification (`tuning`) [[INT-132.A1]] [[INT-129.A2]].

## Changes after ongoing assessment

**2027-02-01, M-2, first cycle.** The frequencies and event triggers held; none is changed. The
cycle cannot judge a frequency: the records that reached the RMF team cover only 2026-11-01 to
2026-11-15 in pre-production, so no family was observed over a full period. What failed was the
delivery the strategy's architecture describes, not the frequency: no monthly roll-up was
compiled, and nothing for December or January reached the PM, the ISSM or the AODR (FND-006,
POAM-024) [[INT-208.A1]]. The console change of 2026-11-04 needs no new trigger, since the drift
scan caught it; it is a change control finding (FND-025) [[INT-208.A1]].

The first measurement results are in `conmon.yaml` `measurement.results`, both outside their
acceptable parameters and reported to the measures' users: MRS-01 (no high closed; the two open
highs are 104 days old against 30) and MRS-02 (88% STIG compliance on the latest scan, against
95%) [[INT-208.A2]]. The tools ran as their upkeep says as far as the fortnight shows (TOOL-02,
TOOL-04, TOOL-05 and the provider's node scan); no TOOL-01 STIG scan and no TOOL-06 external scan
result reached the records [[INT-208.A2]].

<!-- M-2 updates artifacts/data/conmon.yaml when ongoing assessments change a frequency or
     method, appends "## Changes after ongoing assessment" (what changed and why), and adds
     M-2 to touched_by. -->
