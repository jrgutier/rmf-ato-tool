---
artifact_id: ART-POAM
run_id: agent-skeleton
produced_by_task: A-6
touched_by: [A-6]
sources: [ART-SAR, ART-STIG, ART-ORG-CONTEXT, INT-029.A1, INT-029.A2, INT-029.A3, INT-030.A1, INT-030.A2, INT-030.A3]
---
# Plan of action and milestones

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Sensor Gateway | C-1 |
| Acronym | ESG | C-1 |
| System ID | ESG-001 | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | ESG-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: none | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | SP800-53B-MODERATE-SUBSET-6 | S-1 |
<!-- END rmf:facts -->

## How items were derived

The assessment left four open findings, and each has its own item: FND-001 (POAM-001),
FND-002 (POAM-002), FND-003 (POAM-003) and FND-004 (POAM-004) [[ART-SAR]]. The STIG summary
has two open findings, both CAT II and none CAT I. Each is the same weakness as a SAR
finding, so it is named in that item's comments rather than given a second item: STG-001 in
POAM-004 and STG-004 in POAM-003 [[ART-STIG]] [[INT-030.A2]]. The Component requires a
POA&M item for each unit past the 30-day update period, so POAM-005 (esg-north-01) and
POAM-006 (esg-ridge-01) track the two overdue units under FND-004 [[ART-ORG-CONTEXT]]
[[INT-029.A1]]. That gives 6 items: 3 high (POAM-004, POAM-005, POAM-006) and 3 moderate
(POAM-001, POAM-002, POAM-003). The records live in `artifacts/poam/items.yaml`.

## Remediation approach and resources

The PM owns the items that depend on releases and money. Remote update in release 2.2
(POAM-004) and per-technician smart-card accounts in release 2.3 (POAM-001, POAM-003) are
funded in the current ESIT development task order. Release 2.2 also needs the enclave
provider's rule change and the AO's agreement to the new update flow
[[INT-029.A1]] [[INT-029.A2]]. The two overdue units get unscheduled site visits under the
field support contract by 2026-11-20, and the ISSO's rescan is the closing evidence
(POAM-005, POAM-006) [[INT-029.A1]] [[INT-030.A1]]. The ISSM owns the out-of-cycle password
change procedure (POAM-002), due 2026-11-30 [[INT-029.A3]] [[INT-030.A1]]. Until release 2.3,
a site-visit log naming the technician for each maintenance session is reconciled monthly
with the audit records [[INT-029.A2]]. The ISSM reports POA&M status to the AO monthly
[[INT-030.A1]]. The ISSM's provisional residual ratings are moderate for every item except
POAM-002 (low); R-2 makes the final risk determination [[INT-030.A3]].

## Items beyond the organizational remediation period

The Component's 30-day period applies to security-relevant updates [[ART-ORG-CONTEXT]].
POAM-005 and POAM-006 meet it: both overdue units are due to be current by 2026-11-20. The
systemic fix, POAM-004, is scheduled for 2027-01-31. That date depends on release 2.2 and
on approval of the new network flow. Until then the quarterly visits continue, and any
further unit that passes 30 days gets its own item [[INT-029.A1]] [[INT-030.A1]]. POAM-001
and POAM-003 run to 2027-03-31 because release 2.3 is the funded fix. The PM declined to move
it ahead of release 2.2, which addresses the higher risk; the site-visit log is the interim
mitigation [[INT-029.A2]].
