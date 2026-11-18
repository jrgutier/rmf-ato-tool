---
artifact_id: ART-SAP
run_id: 20261118-synthetic-01
produced_by_task: A-2
touched_by: [A-2, M-2]
sources: [INT-142.A1, INT-142.A2, INT-143.A1, INT-143.A2, INT-144.A1, INT-144.A3, INT-146.A1, INT-147.A1, INT-147.A2, INT-147.A3, INT-147.A4, INT-147.A5, INT-148.A1, INT-149.A1, INT-150.A1, INT-151.A1, INT-151.A2, INT-151.A3, ART-SSP, ART-RA, ART-CAT, product/test-results.md#top, ART-CONMON, INT-209.A2]
---
# Security assessment plan

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
<!-- END rmf:facts -->

This plan is a simulated draft in a synthetic run: every answer behind it is SIMULATED, and the
approval below is not a real authorizing official's signature. The structured plan is
`artifacts/data/sap.yaml`; the test strategy it draws on is `artifacts/data/test-strategy.yaml`
[[INT-147.A1]] [[INT-149.A1]].

## Scope and objectives

All 50 controls of the tailored baseline are in scope, security and privacy together; none is
excluded [[INT-151.A2]]. The assessment covers every component in the boundary and the
program-built containers, nodes and database among the inventory items. Its objective is to
determine whether each control is implemented correctly, operating as intended and producing
the desired outcome, so that the AO can decide before the 2027-02-01 MVCR deployment and the
program has the findings it needs for the POA&M [[INT-147.A1]] [[INT-151.A3]]. The level of
effort is three assessors over 17 working days with ERST support and a five-day penetration
test, funded from the FY27 assessment line [[INT-148.A1]].

## Approach and methods

The AODR, for the AO, set three assurance requirements: focused depth and coverage for every
control (AR-001); comprehensive for the controls behind the moderate exfiltration and
re-identification risks and every control the SSP records as partial (AR-002); basic for the two
controls inherited whole, examined against the provider's package (AR-003). The AODR also
directed the sampling after conferring with the SCA [[INT-151.A1]] [[ART-RA]] [[ART-CAT]].

Seventeen procedures (PRC-001 to PRC-017) cover the 50 controls, each method applied to a
control once [[INT-147.A1]]:
- One interview round per role (PRC-001) serves every control.
- Policy and plan controls are examined only (PRC-002, PRC-003).
- Every control implemented in code or configuration is examined and tested, grouped by
  component so that one test account or scan window serves several controls (PRC-004 to
  PRC-016).
- The inherited pe-3 and mp-6 are examined against the cloud provider's package (PRC-017).

Two additional procedures verify requirements outside SP 800-53 that S-3 traced to sa-11 and no
developer test has verified: REQ-11, the DoD IT Standards Registry (APR-001), and REQ-12,
Section 508 accessibility (APR-002) [[INT-147.A5]].

The plan also schedules the items the program left to the assessor [[INT-147.A5]]:
- the Application Security and Development STIG checklist review of the five containers (BM-04);
- a leaver-timing test for ps-4 and ac-2 against out-processing records;
- the PT-3 retest.

## Reuse of test results

Under the Component's reuse limit (365 days, at the required independence), two results are
reused, each with a supplement [[INT-144.A3]] [[INT-147.A2]]:
- **RR-001**, the SCA-witnessed STIG scan of 2026-10-22. Supplemented by the SCA's own scan of
  release 1.5.1.
- **RR-002**, the component red team's penetration test of 2026-10-27 to 2026-10-31, with the
  PT-1 retest. Supplemented by a second penetration test with the CSSP defending.

The AODR approved both after the SCA, the PM and the AODR agreed them [[INT-151.A2]].

The pipeline gates, DT-2 and the account review are the program's own unwitnessed tests. They
are examined as evidence and a sample is re-performed, not reused as results. This uses what
DoDI 8510.01 and DoDI 5000.87 ask programs to offer without lowering the independence the AO
required [[INT-143.A2]] [[INT-147.A2]] [[product/test-results.md#top]].

The test strategy (version 1.1, software pathway, approved by the Component) shares the second
penetration test as a DT and OT event. The operational test agency's January 2027 assessments
come after the out-brief and feed continuous monitoring [[INT-149.A1]] [[INT-150.A1]].

The seven external parts are handled without re-testing the provider [[INT-147.A3]]:
- **The four providers EFRAS inherits from.** The SCA reviewed their agreements and assessment
  packages. Only the EFRAS side of each hybrid control is tested.
- **The three connected systems.** The EFRAS end of each connection is tested, and the
  agreements are examined under ca-3.

## Team and independence

The AODR, acting for the AO, selected the business systems SCA team of the Component's
independent assessment activity for a combined security and privacy assessment. The selection
weighed the team's expertise in IL4 Kubernetes, the managed database, the software factory,
CAC federation, API scoping and the Privacy Overlay [[INT-142.A1]].

The AO required an independent assessment, on the categorization and the risk. Before
deciding, the AO consulted the CIO, the privacy officer for the senior agency official for
privacy and the CISO, and informed the Component OIG's audit liaison. The AO found the team's
independence sufficient [[INT-143.A1]] [[INT-143.A2]]. The CISO verified the qualifications of
the lead and the two team members [[INT-144.A1]].

The privacy office provides part of at-2, pt-2 and pt-3, so it does not assess the privacy
controls itself [[INT-142.A2]] [[INT-146.A1]]:
- the team's privacy-trained assessor assesses the 42 privacy-selected controls;
- the assessor uses the privacy office's methodology and its four metrics: PII outside the SORN,
  purges on time, re-identifiable exports, and breach reports within one hour;
- the privacy officer stays accountable for the privacy assessment and receives the results.

## Schedule

The assessment runs from 2026-11-19 to 2026-12-11 [[INT-147.A4]]:

| Date | Event |
|---|---|
| 2026-11-19 | Kickoff |
| from 2026-11-20 | Interview round |
| 2026-11-23 | SCA scan |
| 2026-11-24 | Container checklist review |
| 2026-11-30 to 2026-12-04 | Penetration test |
| 2026-12-01 | Leaver-timing test |
| 2026-12-02 | DT-2 re-performance |
| 2026-12-03 | REQ-11 and REQ-12 verification |
| 2026-12-07 | Privacy tests |
| 2026-12-11 | Out-brief |

The PM notified the AO, the AODR, the ISSM, the information owner, the privacy officer and the
CSSP on 2026-11-18. The PM also released the resources and gave the team access to the system,
the environment, the documentation, the records, the artifacts and the test results that day
[[INT-148.A1]].

## Rules of engagement

Testing runs only in the pre-production account with synthetic data, built from the production
templates. Nothing runs against production, live data or networks beyond the access point path,
so no interim authorization to test is needed (ART-AUTHREC) [[INT-147.A4]]. The rules:
- scans are authenticated, with accounts the PM issues;
- the ISSO and the CSSP get source addresses and times before every scan and test;
- the ISSM can stop any test;
- a critical finding goes to the ISSM and the AODR within one working day;
- no denial of service, no social engineering, and no data leaves the account.

The penetration test follows NIST SP 800-115. Its scope, threat sources and objectives are in
`sap.yaml` `penetration_test`. ca-8 is not in the 50-control subset, so the test is the
organization's addition [[INT-147.A4]].

## Review and approval

The SCA reviewed the plan. On 2026-11-18 the AODR approved it, acting for the AO under a
delegation that covers assessment plans [[INT-151.A3]]. In the AODR's view, the methods are
deep enough where it matters, and the schedule leaves time for the report, the POA&M and the
risk analysis before the decision.

One constraint: the release 1.5.2 fixes, due 2026-12-10, are verified only if time allows.
Otherwise they stay open findings with POA&M items [[INT-151.A3]].

## Ongoing assessment plan (M-2)

**2027-02-01, first cycle.** The ongoing assessment uses this plan's methods per control
(`sap.yaml`) on the frequencies of the monitoring strategy, with the same assessor team and
independence; `sap.yaml` is not changed [[ART-CONMON]]. Scope this session: cm, ra and ca, the
families whose frequency makes them due and on which the cycle's records bear (at most three
families per session). Also due but carried to the next ongoing assessment session: au, sa, sc,
si, sr (weekly or monthly) and cp-9 (monthly), and the controls whose POA&M milestones fell due
in other families (ac-2, ps-4, pt-3, ia-5, au-11, pl-2, cp-2, ir-8, sc-7, sa-11, ca-3).
Evidence is the monitoring records, which end on 2026-11-15, the change log and interviews;
fixes said to be in release 1.6 are verified only on a scan, retest or record the assessor can
examine, which COND-01 and COND-05 schedule by 2027-02-26 and 2027-03-31 [[INT-209.A2]].
