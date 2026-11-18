---
artifact_id: ART-SSP
run_id: 20261118-synthetic-01
produced_by_task: S-4
touched_by: [S-4, S-6, I-2, A-5, M-1]
sources: [INT-123.A3, INT-123.A4, INT-123.A5, INT-126.A1, INT-127.A1, INT-133.A1, INT-134.A1, INT-134.A2, INT-103.A1, INT-117.A2, INT-118.A1, INT-119.A1, INT-113.A1, INT-116.A1, INT-106.A1, product/conops.md#limitations, product/architecture.md#leveraged, ART-STIG, INT-138.A1, INT-138.A2, INT-139.A1, INT-140.A1, INT-141.A1, INT-177.A4, INT-179.A1, INT-204.A1, INT-205.A1, ART-CHG]
---
# System security plan

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

## Approach to control implementation

The controls are implemented in code and managed services inside the program-owned account:
infrastructure templates and signed images deployed only by the pipeline, CAC sign-in through the
enterprise identity broker, encryption with program-owned keys, and logs forwarded to the CSSP.
Platform, boundary and pipeline controls are inherited in whole or in part from five providers
(below). Each of the 50 selected controls has one statement in `artifacts/ssp/controls/<fam>.yaml`
with its components, tailored parameters, inheritance and evidence: 30 implemented, 14 partial, 4
planned and 2 inherited [[INT-103.A1]] [[product/architecture.md#leveraged]]. The security plan,
the privacy plan and the system C-SCRM plan are consolidated in this artifact, because one small
team keeps all three and their controls overlap; the system description, boundary, inventory,
roles and open items exist once and the other plans point to them (`plan_structure` in
`artifacts/data/ssp-records.yaml`) [[INT-123.A3]]. The C-SCRM plan is
`artifacts/data/scrm-plan.yaml`, approved by the PM on 2026-11-18 after coordination with the
Component C-SCRM program office; it records the S-2 decisions on sr-3 and sr-11, the two critical
suppliers' relationships, monitoring and part in contingency and incident planning, and the
quarterly supply chain report [[INT-123.A4]] [[INT-126.A2]]. The plans are reviewed annually and
with each major release (`artifacts/data/plan-reviews.yaml`) [[INT-123.A3]].

## Privacy plan

The system processes maintainer PII, so this plan holds its privacy plan with the security plan.
It meets the Privacy Act and DoDI 5400.11 duties: collection only under the existing Component
SORN and only its five data elements, notice through the SORN and the sign-in banner, use limited
to the SORN purposes, the PIA (ART-PIA, draft 0.9, approval before production data), retention
and the monthly purge, de-identified exports (fixed in release 1.6), breach response through the
Component privacy office, and the Privacy Overlay's controls (pt-2, pt-3, ra-8, si-12, at-2 and
the privacy parts of ir-6, sc-28 and cm-2). The privacy controls are assessed by examining the
SORN, the PIA and the data map, testing the ingest field filter, the purge job and the
re-identification of a sample export, against four metrics: PII outside the SORN (zero), purges on
time, re-identifiable exports (zero after 1.6) and breach reports within one hour
(`privacy_plan` in `artifacts/data/ssp-records.yaml`). The Component privacy office reviews and
approves the privacy plan before the AO approves the plans at S-6 [[INT-127.A1]] [[INT-106.A1]]
[[product/privacy.md#pia]].

## Inheritance and shared responsibility

- **Example Cybersecurity Service Provider (SVA-001).** Monitors the forwarded logs 24x7, declares
  and categorizes incidents, supports response, reports to JFHQ-DODIN and runs a monthly external
  scan (au-6, si-4, ir-4, ir-6, ra-5, all hybrid). The system forwards its logs, reviews its own
  privileged-action report, contains and recovers inside the account and remediates findings
  [[INT-118.A1]] [[INT-098.A1]].
- **Example GovCloud IL4 region (SVA-002, LA-01).** Implements physical protection and media
  sanitization whole (pe-3, mp-6 inherited) and the snapshot machinery and managed-service
  patching in part (cp-9, si-2 hybrid). The system configures backups and keys, tests restores and
  patches what it builds [[INT-119.A1]] [[INT-117.A1]].
- **Example Enterprise Cloud Access Point (SVA-003).** Protects and inspects the NIPRNet boundary
  (sc-7 hybrid); the system keeps its subnet tiers, WAF and egress allow-list [[INT-113.A1]].
- **Example Software Factory (SVA-004).** Runs the pipeline scans, signs images and vets base images
  (sa-11, sr-3, sr-11 hybrid); the system pins dependencies, admits only signed images and fixes
  what the scans find [[INT-116.A1]].
- **Component privacy office (SVA-005).** Owns the SORN, privacy training and the review of PII
  processing (at-2, pt-2, pt-3 hybrid); the system limits collection and use in code and reports
  breaches [[INT-106.A1]].

## Plan records

`artifacts/data/ssp-records.yaml` holds the values a reviewer checks. Funding: implementation
(about $1.1M in the ERST contract, FY26-FY27), assessment ($180K, FY27), sustainment through
operations ($420K a year, FY27-FY31), configuration management ($150K a year) and vulnerability
management ($120K a year), all programmed; nothing is unfunded [[INT-126.A1]]. Cryptography: TLS
in transit, AES-256 at rest and image signing, each with FIPS 140-validated modules and program-
owned keys in the cloud key service; it is not an NSA-approved solution, and the key management
technology and process are recorded instead [[INT-112.A3]] [[INT-128.A1]]. No user reaches the
system from non-government equipment, so no telework approval is needed; no separate
E-Authentication risk assessment was performed, because every user authenticates with CAC at the
enterprise identity broker [[INT-123.A5]]. Approvals are added at S-6.

## Open items

Each partial or planned control, with its gap and plan; A-6 turns the open findings into POA&M
items.

- **au-11** (partial): the log store keeps 90 days, short of the one-year Component value; the
  CSSP's one-year copy is not the program's. Archive tier in release 1.6 [[INT-090.A3]]
  [[product/conops.md#limitations]].
- **ca-2** (partial since A-5): the first assessment is done and its report delivered; the
  annual assessment of a third of the controls is not yet scheduled [[INT-177.A4]]
  [[INT-179.A1]].
- **ca-3** (partial): the EMIS memorandum of agreement is under legal review and the connection
  runs on an interim e-mail approval; signature targeted 2026-12-31 [[INT-092.A2]].
- **ca-5** (planned): no POA&M yet; A-6 writes it [[INT-092.A3]].
- **ca-7** (planned): the strategy is approved (S-5, S-6) but monitoring has not yet run under it;
  the first cycle follows the authorization decision (updated at I-2) [[INT-092.A3]] [[INT-138.A1]].
- **cm-6** (partial): two program-fixable database STIG items (STG-001 connection logging
  verbosity, STG-002 break-glass role password complexity); release 1.5.2, 2026-12-10; and the
  Application Security and Development STIG review of the containers, owed at assessment (added
  at I-2) [[INT-093.A1]] [[ART-STIG]].
- **cp-2** (partial): the contingency plan (ART-CP) is written but not yet approved or
  distributed; PM approval by 2026-12-15 [[INT-095.A1]] [[INT-126.A2]].
- **cp-4** (partial): only the database restore was tested (DT-2, 3 h 10 min); the regional
  failover and the tabletop have never been held; EX-01 and EX-02 in 2027-02 [[INT-095.A2]]
  [[product/conops.md#limitations]].
- **ia-2** (partial): two break-glass console accounts use FIDO2 keys instead of CAC; the
  deviation goes to the AO, no fix planned; their use follows bypass procedure BYP-01 in the CM
  plan [[INT-097.A1]] [[INT-123.A2]].
- **ia-5** (partial): password complexity of the break-glass database role; release 1.5.2
  [[INT-097.A2]].
- **ir-4** (partial): handling is not yet tied to an approved plan, coordinated with contingency
  planning or followed by a lessons-learned step; ART-IRP approval by 2026-12-15 and the first
  tabletop in 2027-02 [[INT-098.A1]] [[INT-099.A1]].
- **ir-8** (planned): ART-IRP is written in this task; it becomes implemented when the PM approves
  it by 2026-12-15 [[INT-099.A3]] [[INT-126.A2]].
- **pl-2** (partial): the plans are approved with changes (S-6); the PM's approval of the
  contingency, incident response and CM plans is due 2026-12-15, and the privacy risk assessment
  rests on a draft PIA (updated at I-2) [[INT-103.A1]] [[INT-138.A1]].
- **pt-3** (partial): exports and the training extract keep an unsalted DoD ID hash; salted,
  rotated pseudonyms in release 1.6, 2027-01-15 [[INT-106.A2]] [[product/conops.md#limitations]].
- **ra-5** (partial): two high vulnerabilities in CMP-REPORT exceed the 30-day remediation time;
  release 1.5.2, 2026-12-10 [[INT-107.A2]] [[INT-108.A1]].
- **ra-8** (partial): the PIA is a draft; approval by 2027-01-25, before production data
  [[INT-109.A1]] [[ASM-011]].
- **sa-11** (partial): the CMP-REPORT highs and the retest of PT-3 are open, and no test has
  verified REQ-11 or REQ-12 [[INT-111.A1]].
- **si-2** (partial): the 30-day install time was missed for the CMP-REPORT highs; release 1.5.2,
  2026-12-10 [[INT-114.A1]].

## Plan Review and Approval (S-6)

The approvals below are simulated decisions in a synthetic run; they are not a real authorizing
official's signature.

- **Privacy plan.** The Component privacy officer, acting for the senior agency official for
  privacy, reviewed and approved the privacy plan on 2026-11-18, before the plan set went to the
  AODR. The approval keeps two items open: the PIA must be signed before production maintainer
  data is loaded (ra-8), and exports stay re-identifiable until release 1.6 (pt-3)
  [[INT-133.A1]].
- **Security plan and plan set.** The AODR, signing for the AO, reviewed the security plan, the
  privacy plan, the C-SCRM plan and the supporting plans on 2026-11-18. The AODR found them
  complete and commensurate with the risk, and approved them with changes
  (`approvals` in `artifacts/data/ssp-records.yaml`) [[INT-134.A1]]. The changes required:
  - the PM approves the contingency, incident response and configuration management plans by
    2026-12-15 [[INT-126.A2]];
  - the 18 partial and planned controls under Open items go into the POA&M with dates at
    assessment, including the regional failover that has never been tested, which the
    February 2027 exercise must prove [[product/conops.md#limitations]];
  - the PIA is signed before production data.
  None of these changes blocks implementation. The AODR reviews them again before assessment.
- **Continuous monitoring strategy.** The AODR approved the system continuous monitoring
  strategy and its monitoring frequencies on 2026-11-18 (`approval` in
  `artifacts/data/conmon.yaml`). None of those frequencies is looser than the Component
  minimums. A change to the CSSP subscription or to the SIEM forwarding sends the strategy back
  for approval [[INT-134.A2]].
- **What stays open.** The approvals do not change any control's status:
  - pl-2 stays partial until the three supporting plans are approved;
  - ca-7 stays planned until monitoring runs under the approved strategy.
  The plans are next reviewed at the interval in `artifacts/data/plan-reviews.yaml`.

## Update Control Implementation Information (I-2)

The plan set is updated to the as-implemented state as version 1.1 of 2026-11-18, approved
under change management by the configuration control board with the PM in the chair, and logged
in `artifacts/data/plan-reviews.yaml` with the security and the privacy plan [[INT-138.A2]]
[[INT-141.A1]]. The update corrects wording; it changes no control status and no tailored value
the AODR approved, so the counts above stand (30 implemented, 14 partial, 4 planned, 2
inherited) [[INT-138.A1]].

- **What implementation showed.** I-1 recorded the secure configuration state in ART-STIG:
  four benchmarks, no open CAT I item, two open CAT II database items (STG-001 connection
  logging verbosity, STG-002 break-glass database role password complexity, both in release
  1.5.2), four database engine settings and the Kubernetes control plane checks that are the
  cloud provider's, and no Application Security and Development STIG review of the five
  containers yet [[ART-STIG]] [[INT-136.A1]] [[INT-136.A2]].
- **cm-6.** The statement now records the provider-managed items as not applicable to the
  program's configuration, naming the provider, instead of "inherited deviations the ISSM
  approves": only the AO or the AODR approves a configuration exception, and none has been
  approved. It names STG-001 and STG-002 and the container checklist review owed at assessment
  [[INT-138.A1]] [[INT-137.A1]]. Its open item above now names them.
- **pl-2.** The statement now records the privacy officer's and the AODR's approvals of
  2026-11-18; it stays partial for the three supporting plans the PM approves by 2026-12-15 and
  for the draft PIA. Its open item above is updated to match [[INT-134.A1]] [[INT-138.A1]].
- **ca-7.** The statement now states the approved strategy's reporting: a monthly roll-up to
  the PM, the ISSM and the AODR, and a quarterly posture report to the AO. It stays planned until
  the first cycle runs; its open item above is updated to match [[INT-134.A2]] [[INT-138.A1]].
- **As built.** Release 1.5.1 of 2026-11-07 fixed the report export scoping check (PT-1, retest
  pass 2026-11-10) and the verbose server header in pre-production; nothing is in production
  yet, and no inventory item was added or removed [[INT-139.A1]]. The recovery and incident
  mechanisms are built as the contingency and incident response plans describe; only the
  database restore has been tested [[INT-139.A2]].
- **Privacy plan.** Reviewed against the implementation with no change to its content: the
  ingest field filter, the purge and the banner are in place; the PIA is still a draft and the
  exports keep the unsalted hash until release 1.6 (PT-2) [[INT-140.A1]].
- **Unchanged.** Provider arrangements, agreements, interconnections, user groups and
  reciprocity records (no received system) [[INT-138.A3]].
- **For the requirements.** Implementation raised no new security-relevant constraint on the
  requirements; nothing goes back to P-15 [[INT-138.A1]] [[INT-136.A1]].

## Changes from remediation (A-5)

No control was remediated during the assessment: none of the 24 findings has a fix with evidence
the assessor could reassess, so every finding goes to the POA&M at A-6 [[INT-177.A1]]
[[INT-178.A1]]. One statement changed, approved by the configuration control board as version 1.2
of 2026-12-14 and logged in `artifacts/data/plan-reviews.yaml` for the security and the privacy
plan [[INT-179.A1]]:

- **ca-2** moves from planned to partial. The statement predated A-1 and A-2 and still said no
  assessor was selected. It now records the AODR's selection of the independent team and approval
  of the plan on 2026-11-18, the assessment from 2026-11-19 to 2026-12-11 and the report's delivery
  on 2026-12-11; the annual assessment of a third of the controls stays open (FND-003)
  [[INT-177.A4]] [[ART-SAR]].

The control counts are now 30 implemented, 15 partial, 3 planned and 2 inherited. The privacy
plan's content is unchanged [[INT-179.A1]].

## System and Environment Changes (M-1)

Release 1.6 (CHG-003) is a significant change, so the plan is updated with it and the update is
logged as plan change 1.3 of 2027-02-01 in `artifacts/data/plan-reviews.yaml`, approved by the
board and tracked by CHG-003 [[ART-CHG]] [[INT-204.A1]]. Four statements record the release as
deployed to pre-production, each keeping its status (partial) until the SCA verifies the fix:

- **pt-3**: salted, rotated pseudonyms; the retest of 2027-01-20 and the PIA approval of
  2027-01-25 (COND-01); the privacy plan changes with it, and the privacy officer confirmed the
  approved PIA describes the release [[INT-205.A1]].
- **au-11**: the archive tier and the amended CSSP agreement (POAM-019).
- **cm-6**: the STG-001 setting and the container baseline pipeline check (COND-05).
- **ia-5**: the break-glass database password policy and reset (STG-002).

The control counts are unchanged. The pl-2, cp-2 and ir-8 statements still describe the plans as
awaiting the PM's approval, which he gave on 2026-12-15 (POAM-012 to POAM-014); updating them is
plan maintenance owed at M-4, not a change of the system, and is left for that task
[[INT-202.A3]].
