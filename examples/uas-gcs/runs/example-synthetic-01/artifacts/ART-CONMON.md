---
artifact_id: ART-CONMON
run_id: example-synthetic-01
produced_by_task: S-5
touched_by: [S-5, M-2]
sources: [INT-057.A1, INT-057.A2, INT-057.A3, INT-058.A1, INT-058.A2, INT-007.A1, ART-ORG-CONTEXT, ART-RA, ART-SSP, INT-109.A1, INT-110.A1, INT-111.A2, product/monitoring/cycle-2026-10.md#top]
---
# Continuous monitoring strategy

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

## Strategy overview

The station's strategy applies the organizational strategy in ART-ORG-CONTEXT: frequency follows
control volatility, scans run monthly when connected and on reconnection, account reviews are
quarterly, and one third of the remaining controls are assessed each year so every control is
assessed within the authorization period [[ART-ORG-CONTEXT]] [[INT-007.A1]] [[INT-057.A1]].
Monitoring attention goes first to the top risks in ART-RA (TE-5 shared maintenance account,
TE-6 GDT firmware) and to the logs that are not forwarded (TE-8) [[ART-RA]] [[INT-057.A2]].
Automated monitoring covers the workstation and router through the start-up and pre-upload
compliance check and the enclave's collection; the mission planner and GDT are monitored by
hand in the ISSO's weekly review until log forwarding is engineered, so near-real-time
monitoring is not claimed for them [[INT-057.A3]] [[ART-SSP]].

## Monitoring frequencies

`artifacts/data/conmon.yaml` gives all 20 baseline families a frequency, method and owner
[[INT-057.A1]]:

- **continuous:** cm (compliance check before every mission).
- **weekly:** au (ISSO station log review, with a manual check of planner and GDT logs; the
  enclave reviews forwarded logs daily [[INT-058.A1]]).
- **monthly:** ra, sc, si (scans and remediation status when connected and on reconnection).
- **quarterly:** ac, ia, ma, mp (account, authenticator, maintenance and media reviews), and ca
  (ISSM posture review).
- **event-driven:** pe (tamper seal and kit check at receipt and each setup).
- **annually:** at, cp, ir, pl, pm, ps, pt, sa, sr (plans and records reviewed, plans also after
  each exercise or incident).

The ISSO owns most station-level checks, the ISSM the plan and program reviews, and the privacy
officer the pt family [[INT-057.A1]] [[INT-057.A3]].

## Ongoing authorization triggers

The time-driven trigger is 365 days: the AO reviews posture and the year's assessments each
year, three times within the authorization period [[INT-057.A2]]. Events that trigger a review,
as listed in conmon.yaml `ongoing_authorization`: a significant change; a new critical
vulnerability without mitigation; a missed high-risk remediation date; a confirmed incident; a
captured or lost kit; a threat change raising TE-1, TE-3, TE-5 or TE-6 to high [[INT-057.A2]];
and a change to or lapse of the enclave's ATO or brigade services [[INT-058.A2]].

## Reporting

The ISSM reports quarterly to the AO, with the AODR and Component CISO copied, and twice a year
to the risk executive [[INT-057.A3]] [[ART-ORG-CONTEXT]]. Reports carry the organizational
metrics: past-due POA&M items, critical and high vulnerabilities past their remediation period,
STIG compliance, and days since each station's logs last reached the enclave collector
[[INT-057.A3]].

## Roles and tools

The ISSO collects station data (compliance check output, weekly log report, scans) and the SCA
performs the annual assessments [[INT-057.A3]]. The brigade S6 as common control provider
monitors the boundary and intrusion detection continuously, reviews forwarded logs daily, passes
station alerts and scan results through the CSSP within one business day, and sends the ISSM a
monthly summary of its common-control status; it sees nothing from the planner or GDT
[[INT-058.A1]]. The ISSM analyzes and reports [[INT-057.A3]]. Known limits: the weekly review has
run only at test events so far and planner and GDT logs are local only [[INT-057.A3]].

## Changes after ongoing assessment

**M-2, cycle 2026-10 (as of 2026-10-29): the frequencies and triggers held; conmon.yaml is
unchanged.** The first ongoing assessment covered the families due (au, cm, ra, sc, si, pe) on
the cycle's monitoring records [[product/monitoring/cycle-2026-10.md#top]]:

- The weekly au review ran in all four weeks on all six test-range stations, including the
  three disconnected exercise days, with the planner and GDT logs reviewed by hand
  [[INT-109.A1]] [[product/monitoring/cycle-2026-10.md#log-reviews]]. This closes the known
  limit "run only at test events" for the test-range stations; fielded stations are not yet
  shown, so weekly stays the right frequency and no increase is justified.
- The continuous cm check caught and blocked the one drift in the cycle (the 2026-10-14
  screen-lock change on etgcs-p3-ws) before mission upload, so the continuous frequency is
  working as intended [[INT-109.A2]] [[product/monitoring/cycle-2026-10.md#config-checks]].
- The monthly scans (ra, sc, si) found the known GDT and planner vulnerabilities still open and
  no new high or critical finding; they keep tracking the open remediation, so monthly stays
  [[INT-111.A2]] [[product/monitoring/cycle-2026-10.md#vuln-scan]].
- The event-driven pe check ran at all 22 setups with no exception
  [[INT-111.A3]] [[product/monitoring/cycle-2026-10.md#incidents]].
- No event trigger fired: no significant change (M-1), no incident, no new critical
  vulnerability, no threat change, and no high-risk remediation date passed
  [[INT-110.A2]] [[product/monitoring/cycle-2026-10.md#threat-updates]].

No family showed repeated new weaknesses or a stable automated record long enough to justify a
frequency change after one cycle, so PER-ISSM and PER-PM were not asked for a change. The
planner end of support (2027-06) is already covered by the sr review and the release 3.0
significant-change trigger.
