---
artifact_id: ART-AUTHREC
run_id: 20261118-synthetic-01
produced_by_task: A-2
touched_by: [A-2, R-4]
sources: [INT-147.A4, INT-151.A3, product/architecture.md#boundary, INT-198.A1, INT-198.A2]
---
# Authorization ledger

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

## Decisions in force

AUTH-001, an authorization to operate with conditions (AD-ATOC) issued by the AO on 2027-01-25,
terminating 2028-01-25, with conditions COND-01 to COND-06 due between 2027-02-15 and
2027-03-31; the ledger's system status is `ATO-with-conditions`, and the last security review
is the assessment delivered on 2026-12-11. The decision memo is ART-AODM [[INT-198.A1]]
[[INT-198.A2]].

## History (A-2)

At A-2 the ledger held no record and its system status was `none`: the system had never been
authorized, and no interim authorization to test was in force or needed. Every event in the
assessment plan ran in the pre-production account with synthetic data, a separate environment
outside this authorization boundary [[INT-147.A4]] [[product/architecture.md#boundary]]. The
AODR approved the plan on that basis [[INT-151.A3]].
