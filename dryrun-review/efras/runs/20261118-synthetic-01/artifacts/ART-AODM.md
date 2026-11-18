---
artifact_id: ART-AODM
run_id: 20261118-synthetic-01
produced_by_task: R-4
touched_by: [R-4]
sources: [INT-198.A1, INT-198.A2, INT-198.A3, INT-198.A4, INT-197.A1, INT-196.A1, INT-195.A1, INT-190.A1, ART-RAR, ART-POAM, ART-PKG]
---
# Authorization decision

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

## Decision

On 2027-01-25 the authorizing official (PER-AO) issued an **authorization to operate with
conditions** (AD-ATOC), ledger record AUTH-001 in `artifacts/data/authorizations.yaml`, signed
with the AO's PKI certificate [[INT-198.A1]]. The decision was made after the AODR's
recommendation, the privacy officer's coordination of the same day and the risk executive's
input [[INT-197.A1]] [[INT-196.A1]] [[INT-198.A4]]. It is conveyed to the PM as system owner and
to the ISSM, AODR, CISO, privacy officer, information owner, decision authority and user
representative.

## Terms and conditions

Six conditions, each tied to POA&M items; a missed condition date is an event-driven trigger for
the AO's review [[INT-198.A2]]:

- COND-01 (2027-02-26): no real maintainer record in production until the SCA verifies the
  pseudonym fix, the approved PIA and the leaver step (POAM-001, POAM-010, POAM-004, POAM-005).
- COND-02 (2027-02-15): report container rebuilt and rescanned clean (POAM-002, POAM-003,
  POAM-017); otherwise PDF and slide exports are switched off until it is.
- COND-03 (2027-03-05): EMIS data only under the signed agreement (POAM-011).
- COND-04 (2027-03-01): tabletop and regional failover test with the after-action report
  (POAM-009, POAM-015).
- COND-05 (2027-03-31): SCA verification of the configuration fixes (POAM-006, POAM-007,
  POAM-008, POAM-021).
- COND-06 (2027-02-28): monthly POA&M updates and roll-up to the AODR (POAM-023, POAM-024).

## Authorization termination date

2028-01-25, one year, not the three years an ATO may run: the fixes the decision relies on are
met but unverified, and the first monitoring cycle has to show they hold before a longer term or
ongoing authorization [[INT-198.A1]] [[INT-197.A1]].

## Basis for the decision

The AODR's determination in ART-RAR: overall risk moderate, four moderate risks (RSK-001 to
RSK-004) and six low, none high, no open CAT I STIG finding; within the tolerance for operations
and assets, above the low tolerance for individuals while real maintainer data is present
[[ART-RAR]]. The POA&M as of 2027-01-25: most before-authorization milestones met, the report
container and the EMIS agreement slipped, no item yet verified by the SCA [[ART-POAM]]. The PM
reviewed the Component threat assessment of 2026-07-15 on 2027-01-18 [[INT-195.A1]]. The risk
executive's input (the factory dependency as a shared risk; a conditioned authorization preferred
to a slipped fielding) shaped COND-02 and the decision type [[INT-190.A1]] [[INT-198.A4]].

## Residual risk accepted

The AO accepts the residual moderate risk to organizational operations, organizational assets
and individuals on these terms, including the break-glass FIDO2 deviation (RSK-007, POAM-020)
with its compensating measures, and agrees with the POA&M [[INT-198.A3]]. No risk is high, so no
Component CIO concurrence was needed [[ART-RAR]].

## Disclosures

None: `rmf check` reports no degraded reference for this run. The POA&M progress between the
package and the decision is simulated under one stated rule (ASM-025) [[ASM-025]].
