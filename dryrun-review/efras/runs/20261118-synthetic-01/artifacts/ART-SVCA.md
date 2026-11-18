---
artifact_id: ART-SVCA
run_id: 20261118-synthetic-01
produced_by_task: S-4
touched_by: [S-4, M-2]
sources: [INT-060.A3, INT-110.A1, INT-117.A1, INT-117.A2, INT-118.A1, INT-118.A2, INT-119.A1, INT-119.A2, INT-120.A1, INT-120.A2, INT-121.A1, INT-113.A1, INT-116.A1, INT-106.A1, ASM-016, product/architecture.md#leveraged, INT-208.A3]
---
# Cybersecurity service agreements

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

## Agreements

Five providers carry controls the system inherits, and `artifacts/data/service-agreements.yaml`
holds one agreement for each, with its services, both parties' duties and the baseline controls
each service aligns with; the CSSP comes first [[INT-117.A2]].

- **SVA-001, Example Cybersecurity Service Provider (CSSP).** A support agreement of 2026-04-01
  covering log monitoring (si-4, au-6), incident response support (ir-4, ir-6) and vulnerability
  alerts with a monthly external scan (ra-5). The CSSP offers its services as evaluated under the
  DoD O-8530.01-M Evaluator's Scoring Metrics; it is the cybersecurity point of contact with the
  cloud provider [[INT-060.A3]] [[INT-118.A1]] [[INT-118.A2]].
- **SVA-002, Example GovCloud IL4 region.** The Component enterprise cloud contract and the
  EFRAS task order, under DFARS Subpart 239.76, for the platform services; it carries pe-3 and
  mp-6 whole and si-2 and cp-9 in part, through its customer responsibility matrix in eMASS. Its
  leveraged authorization (LA-01) is recorded as an external service whose package the ISSM, the
  mission owner, the PM and the AO reviewed on 2026-11-18 [[INT-117.A1]] [[INT-119.A1]]
  [[INT-119.A2]] [[INT-120.A1]] [[INT-121.A1]].
- **SVA-003, Example Enterprise Cloud Access Point.** Its service-level agreement covers boundary
  protection and inspection (sc-7); the program keeps its own subnets, WAF and allow-list and
  gives notice before opening a port [[INT-113.A1]].
- **SVA-004, Example Software Factory.** Its tenant service-level agreement covers pipeline
  scanning (sa-11) and signed images with supply chain vetting (sr-3, sr-11) [[INT-116.A1]].
- **SVA-005, Component privacy office.** The Component's privacy program issuance assigns it the
  SORN, privacy training and the review of PII processing (at-2, pt-2, pt-3) [[INT-106.A1]]
  [[INT-117.A2]].

The ISSM validated each agreement on the system's side for roles, responsibilities, scope and
applicability (SVA-001 on 2026-04-01, the others on 2026-11-18), and the AO or the AODR approved
each instrument [[INT-117.A2]] [[INT-060.A3]]. The ISSM oversees the providers through their
monthly deliverables and an annual review of each agreement (sa-9) [[INT-110.A1]]. The
enterprise identity broker provides no inherited control; its onboarding approval is recorded as
interconnection IC-3 [[product/architecture.md#leveraged]].

## Cloud service offering

`artifacts/data/cloud.yaml` records the DTM 24-001 and reciprocity details: the AO set Impact
Level 4 for the CUI and maintainer PII the system holds; the offering's DoD provisional
authorization and its conditions; the activity tracking checklist the mission owner and the PM
generated with the CSSP and the AO's office, which the AO validated with no gap; the contract
clauses; the CSSP's duties and visibility; the external assessment process with the red team's
penetration test of 2026-10-27; user activity monitoring kept in DoD hands; and the incident
response split, with the CSSP as point of contact [[INT-121.A1]] [[INT-121.A2]] [[INT-120.A2]]
[[INT-120.A3]] [[INT-118.A2]].

The cloud services connect only through the Example Enterprise Cloud Access Point under the
cloud computing SRG, and the platform is built to the CC SRG and the STIGs [[INT-119.A1]]
[[INT-113.A1]]. Before operational use the system passes cybersecurity test and evaluation in an
emulated environment (pre-production, built from the same templates: DT-2, the penetration test)
and in the live environment once deployed, and goes into production only with an IATT or ATO
[[INT-120.A2]] [[product/architecture.md#leveraged]]. Audit and log records follow the CC SRG
reference architecture: the program's logs go to CMP-LOGS and on to the CSSP, which reviews them
with the access point's traffic logs [[INT-118.A2]].

## Effectiveness

No measurement is due yet: M-2 measures each service of the agreements against its duties and
carries any issue the provider and the program cannot resolve to the Component CIO
[[INT-117.A2]].

### First measurement (M-2, 2027-02-01)

The ISSM measured one or more services under each agreement from the program's side, on the
cycle's records, which end on 2026-11-15 (ASM-026); the records are `effectiveness` entries in
`artifacts/data/service-agreements.yaml` [[INT-208.A3]]:

- SVA-001 (CSSP): SRV-01 log monitoring effective; SRV-03 degraded, because the monthly external
  scan report did not reach the program's records (issue open) [[INT-207.A2]].
- SVA-002 (cloud provider): SRV-05 patching effective (control plane patch of 2026-11-09).
- SVA-003 (access point): SRV-06 degraded on evidence, no inspection report for the cycle (issue
  open).
- SVA-004 (software factory): SRV-07 scanning effective; SRV-08 degraded, the hardened base image
  about three months late, holding the report container fix (issue open, intermediate image
  requested).
- SVA-005 (privacy office): SRV-09 effective.

No issue is beyond the parties to resolve yet, so none is reported to the Component CIO
[[INT-208.A3]].
