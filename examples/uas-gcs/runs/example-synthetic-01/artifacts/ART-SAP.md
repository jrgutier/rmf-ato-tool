---
artifact_id: ART-SAP
run_id: example-synthetic-01
produced_by_task: A-2
touched_by: [A-2]
sources: [INT-065.A1, INT-065.A2, INT-066.A1, INT-066.A2, INT-066.A3, INT-066.A4, INT-066.A5, INT-067.A1, INT-067.A2, product/test-results.md#dt-1]
---
# Security assessment plan

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

## Scope and objectives

The whole tailored baseline is in scope, with no excluded controls (`artifacts/data/sap.yaml`)
[[INT-066.A1]]. For hybrid and inherited controls the assessment covers the system's part and
examines the provider's authorization for the rest [[INT-065.A3]]. The objective is a
determination for every assessment objective, so the AO can judge residual risk. The PER-AODR
asked that the disclosed weaknesses (shared `gcsmaint` account, unscanned mission planner,
planner and GDT logs not forwarded) be assessed explicitly [[INT-067.A1]].

## Approach and methods

Every control is examined against its SSP statement and cited plans; controls with technical
mechanisms (ac, au, cm, ia, sc, si) are also tested on at least two stations, and account and
configuration settings on all six; process controls are assessed by interview with the ISSM,
ISSO, maintainers and brigade S6. Depth is focused and coverage full, per SP 800-53A
[[INT-066.A1]]. The reviewed controls and methods in the OSCAL assessment plan are derived from
the baseline by `rmf build`.

## Reuse of test results

Reused as evidence, not as determinations: DT-1 [[product/test-results.md#dt-1]], the
SCA-witnessed STIG scan and the vulnerability scan of 2026-09-15
[[product/test-results.md#stig-scan]] [[product/test-results.md#vuln-scan]], and the
2026-09-08 account review [[product/test-results.md#account-review]]. Spot STIG and
vulnerability scans on two stations confirm currency, and the SCA reviews the not-reviewed STIG
items itself. No result covers the mission planner STIG or planner and GDT log forwarding;
those are assessed directly [[INT-066.A2]].

## Team and independence

A lead assessor (SCA of record), a technical assessor and a privacy analyst from the Component
privacy officer's staff [[INT-066.A3]]. The team reports to the Component CISO, outside the
program chain and the brigade S6, and none of its members built, operates or documented the
system [[INT-065.A2]].

## Schedule

Kickoff, examination and interviews, observation of the cp-4 and ir-3 tabletops, spot scans
and out-brief, with the SAR draft at the end of the window; the dates are in
`artifacts/data/sap.yaml` [[INT-066.A4]].

## Rules of engagement

Testing only on the six pre-production stations at the test range, never on the enclave, a
fielded station, a powered aircraft or a radiating GDT; assessor accounts created and removed by
the ISSO; 48 hours notice to the ISSM and brigade S6 before scans; the ISSO may halt testing for
safety; no data leaves the test range [[INT-066.A5]].

## Review and approval

The PER-AODR reviewed scope, methods and schedule and found them sufficient [[INT-067.A1]], and
approved the plan as written under the AO's written delegation for assessment plans; open S-6
conditions remain items for the SCA to assess [[INT-067.A2]].
