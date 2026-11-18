---
artifact_id: ART-AUTHREC
run_id: 20261118-synthetic-01
produced_by_task: A-2
touched_by: [A-2]
sources: [INT-147.A4, INT-151.A3, product/architecture.md#boundary]
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
<!-- END rmf:facts -->

## Decisions in force

None. The ledger (`artifacts/data/authorizations.yaml`) holds no record, and its system status
is `none`: the system has never been authorized, and no interim authorization to test is in
force or needed. Every event in the assessment plan runs in the pre-production account with
synthetic data, which is a separate environment outside this authorization boundary; nothing
runs on production, on live data or on a network beyond the access point path the pilot
squadrons already use [[INT-147.A4]] [[product/architecture.md#boundary]]. The AODR approved
the plan on that basis [[INT-151.A3]]. The first record is the authorization decision at R-4.
