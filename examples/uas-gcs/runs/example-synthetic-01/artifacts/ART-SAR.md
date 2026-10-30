---
artifact_id: ART-SAR
run_id: example-synthetic-01
produced_by_task: A-3
touched_by: [A-3, A-4, A-5, M-2]
sources: [INT-109.A1, INT-109.A3, INT-110.A1, INT-111.A1, INT-111.A2, product/monitoring/cycle-2026-10.md#top, INT-096.A1, INT-096.A2, INT-097.A1, product/test-results.md#dt-1, product/test-results.md#stig-scan, product/test-results.md#vuln-scan, product/test-results.md#account-review, product/conops.md#limitations, INT-065.A1, INT-065.A2, INT-065.A3, INT-071.A2, INT-072.A1, INT-074.A3, INT-087.A1, INT-088.A3, INT-089.A3, INT-091.A1, INT-091.A2, INT-092.A1, INT-092.A2, INT-093.A1, INT-094.A1, INT-094.A2, INT-094.A3, INT-095.A1, INT-095.A2]
---
# Security assessment report

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Tactical UAS Ground Control Station | C-1 |
| Acronym | ETGCS | C-1 |
| System ID | ETGCS-REG-SIM-0001 | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | ETGCS-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/MODERATE; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-M | S-1 |
<!-- END rmf:facts -->

## Assessment summary

The assessor, acting independently of the program, assessed every one of the 524 controls in
the resolved baseline under the approved assessment plan, family by family, using examine,
interview and test methods; the SSP's own claims were not taken as evidence. The result mix is
420 satisfied, 69 other-than-satisfied and 35 not-applicable (confirmed by evidence), with 69
open findings (FND-001 to FND-069), none closed during the assessment and none rated high or
very high. Every SSP `partial` statement and every open STIG finding produced an
other-than-satisfied result. The determinations live in `artifacts/sar/results/<fam>.yaml`,
one file per family [[INT-091.A1]] [[INT-092.A1]] [[INT-093.A1]].

## Test results reused

The assessment reused the program's developmental test event DT-1 (2026-07-13 to 2026-07-24):
CAC sign-in, cached sign-in, lockout, screen lock, aircraft link keying, lost-link and port
scans all passed, and the reconnect test showed that planner and GDT logs are not forwarded
[[product/test-results.md#dt-1]]. It reused the SCA-witnessed STIG compliance scan and the
vulnerability scan of 2026-09-15 [[product/test-results.md#stig-scan]]
[[product/test-results.md#vuln-scan]] and the ISSO's 2026-09-08 account review
[[product/test-results.md#account-review]]. The assessor witnessed new integrity tests: an
altered bundle and an unsigned GDT image were rejected and a changed baseline file was flagged
at start-up [[INT-092.A1]]. No rescan has followed the 2026-10 bundle [[INT-091.A1]].

## Findings overview

The findings cluster around five root causes, all disclosed by the program
[[product/conops.md#limitations]]:

- **Shared `gcsmaint` and GDT administrator accounts** (moderate): FND-001, FND-003, FND-004,
  FND-006, FND-009, FND-019, FND-020, FND-027 to FND-035, FND-048, FND-060 and FND-067; actions
  cannot be tied to a person and maintenance access is single-factor
  [[product/test-results.md#account-review]] [[INT-091.A2]].
- **Mission planner and GDT logs not forwarded, monitored or correlated** (moderate): FND-007,
  FND-008, FND-013, FND-041, FND-042, FND-057, FND-064, FND-065 and FND-066; station review
  happens only during test events [[INT-071.A2]] [[INT-072.A1]] [[INT-091.A2]].
- **Open vulnerabilities** (moderate): FND-054, FND-062 and FND-063; the GDT management web
  service flaw (vendor high, reachable only from the station internal network) awaits firmware
  5.2.1 and the planner's library findings have no vendor fix date
  [[product/test-results.md#vuln-scan]] [[INT-087.A1]].
- **Unassessed application hardening and planner end of support** (low to moderate): FND-021,
  FND-058, FND-059, FND-061, FND-068 and FND-069; no SRG check of the planner, flight control
  or video applications, and planner support ends 2027-06 with no replacement selected
  [[INT-074.A3]] [[INT-089.A3]] [[INT-092.A2]] [[INT-093.A1]].
- **Plans and exercises not yet in place**: the contingency plan is unwritten and untested
  (FND-023, FND-025), incident response is untrained, unwritten and untested (FND-036, FND-038,
  FND-040), the IC-1 interconnection agreement is unsigned (FND-010), and the privacy threshold
  analysis is unapproved (FND-051 to FND-053, FND-056).

## Recommendations

Replace `gcsmaint` with per-maintainer accounts and offline CAC sign-in as planned for release
2.4, and change the GDT administrator password under a named custodian
[[product/conops.md#limitations]] [[INT-091.A2]]. Forward planner and GDT logs to the enclave
collector; until then export and review them at each reconnect and run the weekly station
review on every fielded station [[INT-091.A2]]. Field firmware 5.2.1 in the 2026-12 bundle,
rescan all six stations, and record a compensating measure or risk acceptance for the planner
library findings [[INT-091.A1]] [[product/test-results.md#vuln-scan]]. Run the SRG checks of
the planner, flight control and video applications and set a selection date for the release
3.0 planner that leaves time to field it before 2027-06 [[INT-092.A2]] [[INT-093.A1]]. Write
and exercise the contingency and incident response plans, sign the IC-1 agreement and obtain
the privacy threshold analysis approval before the authorization decision [[INT-089.A3]].
Every open finding needs a POA&M item in A-6.

## Executive summary (A-4)

The independent assessment of all 524 baseline controls found 420 satisfied, 69
other-than-satisfied and 35 not-applicable. All 69 findings (FND-001 to FND-069) are open: 38
are rated moderate and 31 low; none is high or very high, and each carries a recommendation in
its family results file [[INT-091.A1]] [[INT-093.A1]]. The system owner's staff confirmed the
facts of every finding and asked for none to be closed [[INT-095.A1]].

The significant findings, all moderate, are:

- shared `gcsmaint` and GDT administrator accounts (FND-001, FND-009, FND-027 to FND-035 and
  related): actions are not attributable to a person [[product/test-results.md#account-review]];
- planner and GDT logs not forwarded or monitored (FND-007, FND-008, FND-064)
  [[INT-091.A2]];
- the open GDT management web service flaw and planner library findings (FND-054, FND-062,
  FND-063) [[product/test-results.md#vuln-scan]];
- planner end of support in 2027-06 with no replacement selected (FND-058, FND-069)
  [[INT-093.A1]];
- unwritten and unexercised contingency and incident response plans (FND-023, FND-036)
  [[INT-089.A3]].

Recommendations that matter most for the authorization decision: field release 2.4
(per-maintainer accounts, offline CAC sign-in, log forwarding); field GDT firmware 5.2.1 in the
2026-12 bundle and rescan all six stations; set the release 3.0 planner selection date; sign
the IC-1 agreement and approve the privacy threshold analysis before the decision; write and
exercise the contingency and incident response plans.

System owner's response (recorded as their perspective, not an assessor conclusion): the
program accepts the findings and their severities, plans release 2.4 for the account and log
findings with a named custodian for the GDT administrator password in the interim, will ask the
AO to accept the planner library risk given internal-network-only exposure, and owes a planner
selection date by 2027-01 [[INT-094.A1]] [[INT-094.A2]] [[INT-094.A3]]. The IC-1 agreement and
the privacy threshold analysis are out for signature but not signed; the installed 2026-10
bundle has not been rescanned and closes nothing yet [[INT-095.A2]].

## Assessment report elements (A-4)

- **Assessor and independence:** the Component's independent SCA team, assigned under the AO's
  delegation; its lead is the SCA of record and signs this report. The team reports to the
  Component CISO, outside the program chain and the inherited-control provider, did not build,
  configure, operate or document the system, and is not program-funded [[INT-065.A1]]
  [[INT-065.A2]].
- **Scope, sites and dates:** every baseline control, the system-specific and system parts of
  hybrid controls; inherited controls rely on the providers' authorizations, checking only the
  system's side [[INT-065.A3]]. Assessment ran under the approved plan [[ART-SAP]] and finished
  on 2026-10-29 [[INT-093.A1]].
- **Methods and depth:** examine, interview and test per [[ART-SAP]]; SSP claims were not taken
  as evidence. The assessor witnessed new integrity tests (altered bundle, unsigned GDT image,
  changed baseline file) [[INT-092.A1]].
- **Test results used and previous results reused:** developmental test event DT-1
  (2026-07-13 to 2026-07-24) [[product/test-results.md#dt-1]]; the SCA-witnessed STIG scan and
  the vulnerability scan of 2026-09-15 [[product/test-results.md#stig-scan]]
  [[product/test-results.md#vuln-scan]]; the 2026-09-08 account review
  [[product/test-results.md#account-review]]. No operational test results exist yet, and no
  rescan followed the 2026-10 bundle [[INT-091.A1]]. The planner, flight control and video
  application SRG checks were not run (FND-021, FND-061) [[INT-092.A2]].
- **Findings detail:** each finding's description, severity, recommendation and status, and
  each determination's evidence summary, live in `artifacts/sar/results/<fam>.yaml`.

## Remediation and reassessment (A-5)

No finding was remediated during the assessment period, so none was reassessed and no
determination changed. The program owner reports that every fix needs a release (2.4), a
firmware bundle (GDT 5.2.1, 2026-12), vendor action or a signature not yet given, none of them a
quick fix with existing resources [[INT-096.A1]]; the contingency and incident response plans
are still drafts with tabletops scheduled for the week of 2026-11-16 [[INT-096.A2]]. The
developer has no new scan, test or configuration record: the 2026-10 bundle is unscanned, GDT
firmware is still 5.1.8 and the application SRG checks have not been run [[INT-097.A1]].

All 69 findings (FND-001 to FND-069) remain open and go to the POA&M at A-6.

## Ongoing assessment 2026-10-29 (M-2)

First monitoring cycle (2026-10-01 to 2026-10-28, six test-range stations), assessed by the SCA
with the independence set at A-1 [[product/monitoring/cycle-2026-10.md#top]].

- **Families assessed:** the families due by `conmon.yaml`: au (weekly), cm (continuous), ra,
  sc, si (monthly) and pe (event-driven, 22 kit setups). Quarterly and annual families are not
  due, since A-3 assessed every family in this period; no POA&M milestone fell due by
  2026-10-29.
- **Result mix of the reassessed controls:** au-4.1, au-6.1, au-12 satisfied, au-6, au-6.3,
  au-10 other-than-satisfied; cm-2, cm-2.2, cm-3, cm-6.1, cm-14 satisfied, cm-5.1, cm-5.5, cm-6
  other-than-satisfied; ra-3, ra-3.3, ra-7 satisfied, ra-5, ra-10 other-than-satisfied; sc-4,
  sc-7, sc-23.3, sc-39 satisfied, sc-5 other-than-satisfied; si-2.2, si-3, si-16 satisfied, si-2,
  si-4, si-4.14, si-4.16, si-4.19 other-than-satisfied; pe-3, pe-6, pe-16 satisfied. All other
  determinations in these families were reused from A-3 as still current. The only changed
  result is ra-7 (other-than-satisfied to satisfied).
- **New findings:** none.
- **Closed findings:** FND-055 (ra-7), on evidence that the A-6 POA&M tracks every open finding
  with milestones and is reviewed monthly [[INT-109.A3]].
- **Still open, with progress noted:** FND-007 and FND-064 (the weekly hand review of GDT and
  planner logs now runs every week, but forwarding has no date and fielded stations are not
  shown) [[INT-109.A1]] [[INT-111.A2]]; FND-019 recurred (2026-10-14 screen-lock change under
  gcsmaint, caught by the pre-upload check, not attributable) [[INT-109.A2]]; FND-054, FND-062 and
  FND-063 (the 2026-10-24 rescan confirmed the workstation and router fixes, but the GDT web
  service vulnerability at firmware 5.1.8 and the two planner library findings remain)
  [[INT-109.A3]] [[INT-111.A1]].
- **Reused evidence:** the automated start-up and pre-upload compliance checks (41 start-ups, 37
  uploads), the SCA-witnessed STIG scan and the integrator vulnerability scan of 2026-10-24, the
  ISSO weekly log reports and quarterly account review, the CSSP's forwarded-log review and
  incident record, the setup log and the ISSM threat update
  [[product/monitoring/cycle-2026-10.md#config-checks]]
  [[product/monitoring/cycle-2026-10.md#stig-scan]]
  [[product/monitoring/cycle-2026-10.md#vuln-scan]]
  [[product/monitoring/cycle-2026-10.md#log-reviews]] [[INT-110.A1]] [[INT-110.A2]]
  [[INT-111.A3]].

Determinations and findings live in `artifacts/sar/results/<fam>.yaml`. The POA&M is updated at
M-3 (FND-055's item is still open there).
