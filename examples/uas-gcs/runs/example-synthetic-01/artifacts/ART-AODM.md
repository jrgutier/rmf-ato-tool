---
artifact_id: ART-AODM
run_id: example-synthetic-01
produced_by_task: R-4
touched_by: [R-4]
sources: [ART-RAR, ART-POAM, ART-ORG-CONTEXT, INT-104.A1, INT-104.A2, INT-104.A3]
---
# Authorization decision

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

## Decision

The AO issues an authorization to operate with conditions (AD-ATOC) on 2026-10-29. The AO
alone made this decision; it was not delegated [[INT-104.A1]]. The record is
`artifacts/data/decision.yaml`.

## Terms and conditions

Five conditions, each tied to its POA&M items in `decision.yaml` [[INT-104.A3]]:

- COND-01 (due 2026-11-30): interim accountability and logging measures.
- COND-02 (due 2027-01-15): GDT firmware 5.2.1 fielded and the stations rescanned.
- COND-03 (due 2026-12-18): contingency, incident response and configuration management plans
  signed and the tabletops held.
- COND-04 (due 2026-12-15): IC-1 agreement and privacy threshold analysis signed.
- COND-05 (whole period): the GDT management service and the mission planner stay on the
  isolated station segment and planner data arrives only through signed bundles.

A missed condition, a new CAT I finding or a risk rated high returns the decision to the AO
for downgrade or denial; the ISSM reports monthly [[INT-104.A3]].

## Authorization termination date

2027-06-30, the mission planner's end of support, inside the three-year maximum
[[INT-104.A2]] [[ART-ORG-CONTEXT]].

## Basis for the decision

The AODR's analysis in ART-RAR determines the overall risk moderate, with four moderate and
five low risks and none high [[ART-RAR]]. The worst weaknesses, shared maintenance accounts and
local-only logs, are funded and scheduled in Release 2.4 for 2027-03-31; every open finding has
a POA&M item; no CAT I finding is open; the assessment was independent [[INT-104.A1]]
[[ART-POAM]].

## Residual risk accepted

The AO accepts moderate residual risk on behalf of the mission owner, inside the tolerance that
needs no Component CIO concurrence [[INT-104.A1]] [[ART-ORG-CONTEXT]]. This explicitly includes
the planner library flaws with no vendor fix, accepted under COND-05 [[INT-104.A3]].

## Disclosures

None: `rmf check` reports no degraded reference for this run, and the decision is simulated
in a synthetic run [[INT-104.A1]].
