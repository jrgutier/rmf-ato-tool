---
artifact_id: ART-SAR
run_id: 20261118-synthetic-01
produced_by_task: A-3
touched_by: [A-3]
sources: [ART-SAP, ART-SSP, ART-STIG, product/test-results.md#top, INT-152.A3, INT-160.A2, INT-162.A2, INT-165.A1, INT-167.A2, INT-169.A2, INT-171.A2, INT-172.A1, INT-172.A2, ASM-020, ASM-021, ASM-022, ASM-023, ASM-024]
handling: CUI
---
# Security assessment report

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

## Assessment summary

The business systems SCA team of the Component's independent assessment activity assessed all
50 controls of the tailored baseline, the privacy controls included, against the plan the AODR
approved on 2026-11-18, from 2026-11-19 to the out-brief of 2026-12-11, with NIST SP 800-53A
procedures (`artifacts/data/sar-report.yaml`) [[ART-SAP]]. Each control was examined,
interviewed and, where the plan said so, tested at the plan's depth and coverage; the privacy
controls were assessed by the team's privacy-trained assessor under the privacy office's
methodology [[ART-SAP]] [[INT-171.A2]]. Everything was assessed in the pre-production account,
built from the production templates, with synthetic data; production holds no release yet
(`artifacts/data/sar-summary.yaml`) [[ART-SAP]] [[product/test-results.md#top]].

Result mix: 28 controls satisfied and 22 other-than-satisfied, with 24 open findings, FND-001
to FND-024 (9 moderate, 15 low; none high). The determinations, one per control with a result
for every determination statement, live in `artifacts/sar/results/<family>.yaml`; this report
names them only by finding [[ART-SSP]]. Every control the plan records as partial or planned
is other-than-satisfied; beyond those, test results made controls such as ps-4 and cm-8
other-than-satisfied and an unverified fix made sc-7 so; the inherited pe-3 and mp-6 are satisfied on the cloud provider's own assessment
[[INT-152.A3]] [[INT-169.A2]].

Six results rest on an assumption instead of on evidence, because the product holds no basis
for them: the leaver notification times (ASM-020), the ASD STIG checklist review (ASM-021),
the second penetration test week and the PT-3 retest (ASM-022), REQ-11 and REQ-12 (ASM-023),
and release 1.5.2 (ASM-024). None asserts a pass or a specific failure [[ASM-020]] [[ASM-021]]
[[ASM-022]] [[ASM-023]] [[ASM-024]].

Privacy: of the 42 privacy-relevant controls, the weaknesses that bear on maintainer PII are
FND-018 (re-identifiable exports), FND-020 (no approved PIA), FND-001 and FND-017 (leaver
access) and FND-016 (draft PIA in the plans). The privacy officer, for the senior agency
official for privacy, provides the privacy results to the AO with the report at A-4
[[INT-171.A2]] [[INT-152.A3]].

## Test results reused

- **RR-001**, developmental test, 2026-10-22: the SCA-witnessed Kubernetes and PostgreSQL STIG
  scan of pre-production, reused for cm-2 and cm-6 and supplemented by the SCA's own scan of
  release 1.5.1 on 2026-11-23, which confirmed STG-001 and STG-002 open and found nothing new
  [[product/test-results.md#top]] [[INT-160.A2]] [[ART-STIG]].
- **RR-002**, developmental test, 2026-10-27 to 2026-10-31 (PT-1 retested 2026-11-10): the
  Component red team's penetration test, reused for ac-3 (PT-1 closed), pt-3 (PT-2, re-performed
  on 2026-12-07 with the same result) and sc-7 (PT-3, retest not demonstrated) [[INT-171.A2]]
  [[ASM-022]].
- The program's own pipeline gates of 2026-10-20 and DT-2 (2026-10-06 to 2026-10-17) were
  examined and partly re-performed, not reused as results (12 DT-2 cases and the restore re-run
  on 2026-12-02, each with the DT-2 result) [[INT-172.A2]] [[INT-162.A2]].
- External providers, each confirmed against its own assessment, not re-assessed
  [[ART-SAP]]:
  - **EXT-001**, Example GovCloud IL4 region, commercial, third-party assessment behind the
    DoD provisional authorization and the AO's authorization of 2024-09-18: basis of pe-3 and
    mp-6, and the provider parts of cp-9 and si-2.
  - **EXT-002**, Example Enterprise Cloud Access Point, Component assessment for its
    authorization of 2025-01-10: the NIPRNet part of sc-7.
  - **EXT-003**, Example Software Factory, independent assessment for its authorization of
    2025-10-01, one open POA&M item (the late hardened base image): parts of sa-11, sr-3, sr-11.
  - **EXT-004**, Example Cybersecurity Service Provider, Component assessment and DoD
    O-8530.01-M evaluation, service under its authorization of 2026-04-01: parts of au-6,
    si-4, ir-4, ir-6 and ra-5.
  - **EXT-005**, enterprise identity broker, its own authorization; onboarding approval of
    2026-05-12: CAC assertions for ia-2.
  - **EXT-006**, EMIS, its own authorization of 2025-04-22; interconnection on an interim
    approval (ca-3, FND-004).
  - **EXT-007**, supply status service, its own authorization of 2024-11-05; agreement signed
    2026-06-30 (ca-3).

## Findings overview

The most significant weaknesses, all moderate [[INT-152.A3]] [[INT-171.A2]] [[INT-172.A1]]:

- **FND-018** (pt-3): de-identified exports and the training extract are re-identifiable through
  an unsalted DoD ID hash, re-performed with 50 ID numbers; fix in release 1.6 (2027-01-15).
- **FND-019** (ra-5) and **FND-024** (si-2): two high vulnerabilities in example-imagelib 2.9.1
  in efras-report, open since 2026-10-20 and past the 30-day time, waiting on the software
  factory's hardened base image; release 1.5.2 not verified.
- **FND-001** (ac-2) and **FND-017** (ps-4): leavers' accounts stay active until the inactivity
  disable or the quarterly review; no notification reaches the account manager.
- **FND-007** (cm-6, STG-001) and **FND-013** (ia-5, STG-002): two program-fixable PostgreSQL
  STIG items open, fix in release 1.5.2.
- **FND-008** (cm-6): no documented secure configuration for the five application containers.
- **FND-011** (cp-4): regional failover never tested and no tabletop held.

The low findings record plans and approvals still owed (FND-003, FND-010, FND-015, FND-016,
FND-020), work that later RMF tasks complete (FND-005, FND-006), retention and inventory gaps
(FND-002, FND-009), the EMIS agreement (FND-004), the break-glass deviation (FND-012), and
verification still owed (FND-014, FND-021, FND-022, FND-023) [[INT-165.A1]] [[INT-167.A2]]
[[ASM-023]].

## Recommendations

- Ship release 1.6 with salted, rotated pseudonyms and retest re-identification before any
  production data flows; until then limit exports and the training extract (FND-018)
  [[INT-171.A2]].
- Deploy release 1.5.2 as soon as the factory's base image arrives, rescan, and agree an interim
  image path with the factory for a late base image (FND-019, FND-024, FND-007, FND-013)
  [[INT-172.A1]] [[ASM-024]].
- Feed squadron departures to the account manager with a timestamp and disable within the set
  time (FND-001, FND-017) [[INT-152.A3]] [[ASM-020]].
- Establish and review a documented configuration for the five containers against the ASD STIG
  (FND-008) [[ASM-021]].
- Have the PM approve the contingency, incident response and configuration management plans by
  2026-12-15, hold the combined tabletop and failover test, and complete the PIA before
  production (FND-010, FND-011, FND-014, FND-015, FND-016, FND-020) [[INT-165.A1]]
  [[INT-167.A2]].
- Retest the sandbox egress and verify REQ-11 and REQ-12 in the next DT event before the
  authorization decision (FND-021, FND-022, FND-023) [[INT-169.A2]] [[INT-172.A2]].
