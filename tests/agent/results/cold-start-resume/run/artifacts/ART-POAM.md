---
artifact_id: ART-POAM
run_id: agent-cold-start-resume
produced_by_task: A-6
touched_by: [A-6]
sources: [ART-SAR, ART-STIG, ART-ORG-CONTEXT, INT-023.A1, INT-023.A2, INT-024.A1, INT-024.A2]
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
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-6 | S-1 |
<!-- END rmf:facts -->

## How items were derived

The assessment left three findings open, FND-001 (ac-2), FND-002 (ia-2) and FND-003 (si-2), and
each has one item: POAM-001, POAM-002 and POAM-003 [[ART-SAR]]. The STIG summary has two open
findings, both CAT II and no CAT I: STG-001 is the same weakness as FND-003 and STG-004 the same
as FND-002, so they are named in the comments of POAM-003 and POAM-002 instead of getting items
of their own [[ART-STIG]] [[INT-024.A1]] [[INT-024.A2]]. The result is 3 items: 1 high and 2
moderate; the records are in `artifacts/poam/items.yaml`.

## Remediation approach and resources

POAM-003 closes with release 2.2 (remote update over the uplink), funded in the current
development contract; until it is fielded, out-of-cycle site visits keep every unit within the
30-day update period, which lowers the residual risk to moderate [[INT-023.A1]] [[INT-024.A1]].
POAM-001 and POAM-002 share one fix, release 2.3 with per-technician accounts and smart-card
login, which needs card readers and about two developer-months from the FY27 budget line; until
then a site-visit sign-in log and a password change on each technician departure partly restore
accountability [[INT-023.A2]] [[INT-024.A2]]. The PM owns all three items; the ISSM tracks the
milestones, reviews the POA&M monthly with the PM and reports status to the AO each month
[[INT-024.A2]].

## Items beyond the organizational remediation period

The organization requires security-relevant updates within 30 days or a POA&M item
[[ART-ORG-CONTEXT]]. POAM-003's final milestone (2026-12-31) is past that period because release
2.2 needs the uplink change and a regression test cycle; the PM's interim site visits bring the
two lagging units back inside the period by 2026-11-14 [[INT-023.A1]]. POAM-001 and POAM-002 run
to 2027-03-31, the earliest date the FY27 funding and the card-reader delivery allow; the
organization sets no period for account weaknesses, and the PM accepts the date with monthly
reporting to the AO [[INT-023.A2]].
