---
artifact_id: ART-AUTHRPT
run_id: example-synthetic-01
produced_by_task: R-5
touched_by: [R-5]
sources: [ART-AODM, INT-105.A1, INT-105.A2, INT-106.A1]
---
# Authorization report

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Tactical UAS Ground Control Station | C-1 |
| Acronym | ETGCS | C-1 |
| System ID | ETGCS-REG-SIM-0001 | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | ETGCS-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/MODERATE; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-M | S-1 |
<!-- END rmf:facts -->

## Decision reported

The AO issued AD-ATOC (authorization to operate with conditions) on 2026-10-29, with
authorization termination date 2027-06-30, residual risk moderate, and conditions COND-01
(due 2026-11-30), COND-02 (due 2027-01-15), COND-03 (due 2026-12-18), COND-04 (due 2026-12-15)
and COND-05 (whole period) [[ART-AODM]]. The AODR, acting for the AO, reports it to the
Component CISO, the Component privacy officer, the milestone decision authority and the
enclave's common control provider [[INT-105.A1]].

## Significant deficiencies reported

The organization's threshold is a risk rated moderate or higher, or one the AO accepted
explicitly [[INT-105.A1]]. Reported: RSK-001 (shared privileged accounts, POAM-001 and its
related items, STG-001 and STG-002), RSK-002 (local-only and unreviewed logs), RSK-003 (known
GDT and planner vulnerabilities, POAM-054, POAM-062, POAM-063, including the planner library
flaws without a vendor fix accepted under COND-05) and RSK-005 (plans not written or tested)
[[ART-AODM]] [[INT-105.A1]]. No privacy risk meets the threshold [[INT-105.A1]].

## Operational awareness

The ISSM sends the risk notice with the decision to each fielding unit's commander and to the
enclave's cyber operations lead, listing the COND-05 operating restrictions and the log export
at reconnect; maintainers receive it in the reconnect checklist. Each condition reports back to
the AO when it closes, and the monthly POA&M report shows the open ones [[INT-106.A1]].

## Registry annotation

The AODR annotates the system's registry entry (ART-REG) on 2026-10-29: authorized to operate
with conditions, termination date 2027-06-30, five conditions, residual risk moderate; it is
updated when a condition closes or the decision changes [[INT-105.A2]].
