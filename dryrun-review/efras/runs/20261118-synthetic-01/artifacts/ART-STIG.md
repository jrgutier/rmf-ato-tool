---
artifact_id: ART-STIG
run_id: 20261118-synthetic-01
produced_by_task: I-1
touched_by: [I-1, A-3]
sources: [product/test-results.md#stig-scan, product/test-results.md#pipeline-1-5, product/architecture.md#configuration, INT-135.A1, INT-135.A2, INT-135.A3, INT-136.A1, INT-136.A2, INT-137.A1, ASM-018, ASM-019, INT-160.A2, INT-161.A1, ASM-021, ASM-024]
handling: CUI
---
# STIG and SRG summary

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

## Applicability

Four benchmarks cover the inventory items that need a secure configuration; the records live
in `artifacts/data/stig-summary.yaml` [[product/architecture.md#configuration]] [[INT-135.A1]].

- **BM-01, Kubernetes STIG**: the worker node image INV-009, scanned, and the managed
  Kubernetes service INV-008, whose control plane settings the provider configures under its
  IL4 provisional authorization [[product/test-results.md#stig-scan]] [[INT-137.A1]].
- **BM-02, PostgreSQL STIG**: the managed PostgreSQL database INV-010, as far as the managed
  service lets a tenant configure it [[product/test-results.md#stig-scan]] [[INT-135.A2]].
- **BM-03, the software factory's hardened base image standard**: the container base image
  INV-007, hardened by the factory and taken as delivered; a supplier guide inherited with the
  factory's ATO, not a checklist the program ran [[INT-136.A2]] [[INT-135.A1]].
- **BM-04, Application Security and Development STIG**: the five application containers
  INV-002 to INV-006. No checklist review is recorded for release 1.5.0; the ISSE asks the
  assessor to perform it at A-3, so it stands as not reviewed [[INT-136.A2]] [[INT-135.A3]] [[ASM-019]].

Not applicable: the open-source libraries INV-015 (inside efras-report) and INV-016 (inside
efras-api) have no STIG or SRG of their own; they are covered through their containers under
BM-04 and by the pipeline dependency scan [[INT-135.A3]]. The managed services of kind
`service` (load balancer, object storage, keys, logging, notebooks) are configured by the
program through the templates and the policy checks and otherwise inherited from the cloud
provider, which applies the STIGs to its managed services [[INT-137.A1]] [[product/test-results.md#pipeline-1-5]].

The STIG release numbers are not in the product material; the summary records each as the
release current on the scan date [[ASM-018]].

## Scan results

One compliance scan ran for release 1.5.0: the SCA-witnessed scan of 2026-10-22 on the
pre-production cluster, built from the same templates as production, with the Component
enterprise SCAP STIG scanner named in the configuration management plan's tools
[[product/test-results.md#stig-scan]] [[INT-135.A1]].

| Benchmark | Item | Result | Open | Recorded as inherited |
|---|---|---|---|---|
| BM-01 Kubernetes STIG | INV-009, INV-008 | 94% compliant | 0 program items | the open control plane checks, provider-managed |
| BM-02 PostgreSQL STIG | INV-010 | 88% compliant | 2 (STG-001, STG-002) | 4 (STG-003 to STG-006) |
| BM-03 base image standard | INV-007 | no compliance scan; pipeline image scan only | — | — |
| BM-04 ASD STIG | INV-002 to INV-006 | not reviewed | — | — |

By category: CAT I none; CAT II six PostgreSQL records, two `open` and four `not-applicable`
to the program's configuration (provider-managed); CAT III none [[INT-135.A2]]. The open
Kubernetes control plane items are not itemized in the summary: the product reports them only
as a share of the scan, all provider-managed and marked inherited, and none on the worker
nodes [[product/test-results.md#stig-scan]] [[INT-135.A2]]. The rule IDs of the PostgreSQL
records are placeholders for the IDs in the scan export [[ASM-018]].

The pipeline gates of release 1.5.0 are vulnerability scans, not configuration checklists;
they found the two high vulnerabilities of example-imagelib 2.9.1 in efras-report, which the
SSP and the POA&M carry under ra-5 and si-2, not here [[product/test-results.md#pipeline-1-5]].

## Open findings

No CAT I finding is open [[INT-135.A2]].

- **STG-001** (CAT II, INV-010, cm-6): connection logging verbosity below the STIG value.
  Fix in release 1.5.2, planned 2026-12-10, then rescanned [[product/test-results.md#stig-scan]] [[INT-135.A2]].
- **STG-002** (CAT II, INV-010, ia-5): password complexity of the local break-glass database
  role short of the STIG rule. Fix in release 1.5.2, planned 2026-12-10 [[product/test-results.md#stig-scan]] [[INT-135.A2]].

Both are already disclosed as partial in the approved plan (cm-6, ia-5) and are owed a POA&M
item at A-6 [[INT-136.A1]].

## Accepted deviations

None. No deviation from a benchmark has been approved as an exception by the AO or the AODR.
The four PostgreSQL items and the Kubernetes control plane items that the scan marks inherited
are the provider's settings under its IL4 provisional authorization, configured to the STIGs
and assessed in the provider's own assessment; they are recorded as not applicable to the
program's configuration, naming the provider, rather than as program deviations
[[INT-136.A1]] [[INT-137.A1]]. The approved plan's cm-6 statement calls them "inherited
deviations the ISSM approves"; I-2 corrects that wording [[INT-136.A1]].

## Assessor verification (A-3)

The SCA team witnessed the 2026-10-22 scan and reused it as RR-001 for cm-2 and cm-6, then ran
its own authenticated scan of release 1.5.1 on 2026-11-23 over the worker nodes, the images and
the database instance in pre-production. That scan gave the same result for BM-01 and BM-02:
STG-001 and STG-002 confirmed open, STG-003 to STG-006 confirmed as provider settings the
managed service does not let the tenant configure, and no new item [[INT-160.A2]]
[[product/test-results.md#stig-scan]]. The open items stand in the SAR as FND-007 (cm-6) and
FND-013 (ia-5); release 1.5.2, which carries their fix, was not verified during the assessment,
so neither status changed and `artifacts/data/stig-summary.yaml` is not rewritten [[ASM-024]].

The assessor's Application Security and Development STIG checklist review of INV-002 to INV-006
(BM-04) on 2026-11-24 had no documented secure configuration of the containers to compare
against, so it produced no rule result; BM-04 stays "not reviewed", and the absence of an
established configuration is FND-008 (cm-6) [[INT-161.A1]] [[ASM-021]]. BM-03 was not scanned;
the factory's base image is taken as delivered under its ATO, and the late base image behind the
two efras-report highs is assessed under ra-5 and si-2 (FND-019, FND-024), not as a STIG item
[[product/test-results.md#pipeline-1-5]].
