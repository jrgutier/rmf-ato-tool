---
artifact_id: ART-SECRPT
run_id: 20261118-synthetic-01
produced_by_task: M-5
touched_by: [M-5]
sources: [INT-212.A1, INT-212.A2, INT-212.A3, INT-213.A1, INT-213.A2, INT-213.A3, INT-214.A1, INT-215.A1, INT-216.A1, INT-208.A2, INT-208.A3, INT-210.A1, INT-211.A2, INT-211.A3, ASM-026, ART-CONMON, ART-SAR, ART-POAM, ART-RAR, ART-CHG, ART-SSP, ART-SD, ART-ORG-CONTEXT]
---
# Security and privacy posture report

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

## Reporting period and recipients

SPR-001 is the first posture report. It covers the first monitoring cycle after the
authorization, from 2026-11-01 to 2027-01-31, and was issued on 2027-02-01, marked CUI. The
monitoring strategy sets a quarterly report to the AO, the AODR, the PM and the ISSM. SPR-001
also serves as the first monthly roll-up that COND-06 asks for [[INT-212.A1]] [[ART-CONMON]].

The records behind it end on 2026-11-15 and come from the pre-production account, which is
outside the boundary but built from the same templates. Nothing is deployed to production, and no
monitoring record from December or January reached the program. The report is the posture those
records show, not a quiet quarter [[ASM-026]] [[INT-212.A1]].

The system's GENSER designation names CDRUSSTRATCOM and DISA as the bodies that receive POA&M
updates where they require them. No body has required them, so the report goes only to the four
recipients. The records are in `artifacts/data/posture-reports.yaml` [[INT-212.A3]].

## Posture summary

The ongoing assessment of 2027-02-01 (cm, ra and ca) leaves 27 controls satisfied and 23
other-than-satisfied. cm-3 moved to other-than-satisfied with FND-025, and no finding closed
[[ART-SAR]]. Both security measures are outside their limits [[INT-208.A2]]:

| Measure | Value | Limit |
|---|---|---|
| Mean time to remediate high findings (MSR-01) | 104 days (the age of the two open efras-report highs) | 30 days |
| STIG compliance (MSR-02) | 88% | 95% |

Of the provider services [[INT-208.A3]]:

- Four are effective: SRV-01, SRV-05, SRV-07 and SRV-09.
- Three are degraded, each with an issue open with the provider:
  - SRV-03: the CSSP's external scan report did not reach the program.
  - SRV-06: no inspection report from the access point.
  - SRV-08: the factory's base image is late.

The privacy posture rests on keeping real maintainer records out of the system (COND-01). The
re-identification fix is said to be in release 1.6 but is not yet verified [[INT-214.A1]].

## Changes since the last report

This is the first report, so it lists every change since the start of the period
[[ART-SSP]] [[ART-CHG]] [[ART-POAM]] [[ART-SAR]]:

- **Plan changes.** Versions 1.1 (I-2, 2026-11-18), 1.2 (A-5, 2026-12-14) and 1.3 (M-1,
  2027-02-01, release 1.6).
- **System changes:**
  - CHG-001, an unauthorized console change in pre-production, reverted within the hour.
  - CHG-002, the provider's control plane patch.
  - CHG-003, release 1.6, approved 2027-01-15 and deployed to pre-production only.
- **Assessment results.** New finding FND-025 (cm-3, low).
- **POA&M:**
  - New items POAM-025 (FND-025) and POAM-026, with the analysis record VUL-001 for the medium
    vulnerability in efras-api.
  - POAM-021 is delayed and POAM-012's PIA reference is moved.
  - POAM-020 is risk-accepted in AUTH-001.
  - No item is completed.

Open items: 25 of 26.

## Risks and planned responses

Overall risk stays moderate, and no likelihood, impact or risk level changed [[INT-210.A1]].

- **RSK-004.** FND-025 joined it, and the response adds a read-only network console role, due
  2027-03-12.
- **RSK-002.** The report container fix is not yet carried out. It is due 2027-02-15 under
  COND-02; if the date is missed, the PDF and slide exports are switched off.
- **RSK-001, RSK-003 and RSK-004.** Their timelines passed with no verified effect. They go back
  to implementation and are moved to COND-01 (2027-02-26) and COND-05 (2027-03-31).

No new risk is accepted [[INT-211.A3]].

## Matters for ongoing authorization

The conditions stand as follows on 2027-02-01. None is met and none is overdue [[INT-211.A2]]:

- COND-02 (2027-02-15) is the first at risk.
- COND-01 (2027-02-26), COND-04 (2027-03-01), COND-03 (2027-03-05), COND-06 (2027-02-28) and
  COND-05 (2027-03-31) are open.

No trigger for reauthorization is reached and the PM asks for no new risk acceptance. The AO
should weigh three things [[INT-212.A2]]:

- the two measures outside their limits;
- the three degraded provider services;
- the gap in monitoring records from 2026-11-16 onward.

Records left stale for M-4 (Authorization Updates, deferred in this run): the pl-2, cp-2 and
ir-8 statements and the incident response plan still read as before the PM's plan approvals of
2026-12-15. The cm-3 statement still says every change goes through the pipeline, which FND-025
contradicts [[ART-SSP]] [[ART-SAR]].

## Status to DoD bodies

No body named by the GENSER designation required POA&M updates or vulnerability coordination, so
none was sent outside the recipients [[INT-212.A3]]. What was reported in the period
[[INT-213.A1]] [[INT-213.A2]] [[ART-CHG]] [[ART-POAM]]:

- **Scorecard.** The system's figures were submitted on 2027-02-01. VDP metrics: none, because
  no VDP report was received.
- **Vulnerability status.** POAM-020 is reported as risk-accepted.
- **Directed actions, outside findings and external services.** None to report: no directed
  action and no outside finding was received, and no external service changed status.
- **CMRS.** No statistics are owed, because AUTH-001 is not a continuous authorization.
- **How the data is shared.** It is kept in eMASS and shared up to the Component and with peer
  programs on the risk board through its automated views.
- **DODIN awareness.** The monitoring strategy gives awareness of threats, traffic and employee
  use. It does not give awareness of faults, performance, bandwidth, routes or network
  management on the access point path. That gap is reported and goes to P-7.

Supply chain (the quarterly C-SCRM summary of the SCRM plan) [[INT-213.A3]]:

- **Supplier monitoring.** The factory's base image is about three months late (SRV-08), the
  CSSP's scan report is missing (SRV-03), and the provider patched on time.
- **Open supply chain findings.** POAM-002, POAM-003 and POAM-017.
- **SBOM vulnerabilities.** Two highs in efras-report and one medium in efras-api.
- **Urgent conditions.** None.

## Privacy reporting

EFRAS processes PII, so its privacy status follows the Component's path [[INT-214.A1]]:

- **Path.** From the privacy office to the PCLO, through the Senior Component Official for
  Privacy, to the Chief of the Defense Privacy, Civil Liberties and Transparency Division.
- **What EFRAS feeds.** The semiannual Section 803 report and the FISMA privacy inputs, with its
  PIA status, its SORN coverage and the re-identification finding (FND-018).
- **Protection of the system of records.** The privacy officer does not report it as one whose
  PII cannot be appropriately protected, because no real maintainer record is in the system while
  COND-01 holds. If real records were loaded first, it would be reported to the DoD SAOP.

## Organization tier review

On 2027-02-01 the risk executive (function) and the CISO reviewed SPR-001 with the aggregate
POA&M position: 25 open items [[INT-215.A1]] [[INT-216.A1]].

- **The risk board** finds the position within tolerance while the conditions hold. It tracks the
  factory's late base image as a portfolio risk, and expects the exports switched off if COND-02
  is missed [[INT-216.A1]].
- **The CISO** accepts the report but finds that it does not yet show effective controls in
  operation. The CISO sends two points to the organization's monitoring strategy (P-7)
  [[INT-215.A1]] [[ART-ORG-CONTEXT]]:
  - monitoring records from the deployed environment reach the system owner monthly;
  - the strategy assigns DODIN awareness of faults, performance, bandwidth, routes and network
    management for cloud systems behind the access point.
