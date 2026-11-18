---
artifact_id: ART-SSP
run_id: 20261118-synthetic-01
produced_by_task: S-4
touched_by: [S-4, S-6]
sources: [INT-123.A3, INT-123.A4, INT-123.A5, INT-126.A1, INT-127.A1, INT-133.A1, INT-134.A1, INT-134.A2, INT-103.A1, INT-117.A2, INT-118.A1, INT-119.A1, INT-113.A1, INT-116.A1, INT-106.A1, product/conops.md#limitations, product/architecture.md#leveraged]
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
- **ca-2** (planned): no assessor and no assessment yet; A-1 and A-2 follow [[INT-092.A1]].
- **ca-3** (partial): the EMIS memorandum of agreement is under legal review and the connection
  runs on an interim e-mail approval; signature targeted 2026-12-31 [[INT-092.A2]].
- **ca-5** (planned): no POA&M yet; A-6 writes it [[INT-092.A3]].
- **ca-7** (planned): no system continuous monitoring strategy yet; S-5 writes it [[INT-092.A3]].
- **cm-6** (partial): two program-fixable database STIG items (connection logging verbosity,
  break-glass role password complexity); release 1.5.2, 2026-12-10 [[INT-093.A1]].
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
- **pl-2** (partial): the plans are written in this task and await approval at S-6; the privacy
  risk assessment rests on a draft PIA [[INT-103.A1]].
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
