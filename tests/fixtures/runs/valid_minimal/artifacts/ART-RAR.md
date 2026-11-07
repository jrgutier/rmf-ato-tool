---
artifact_id: ART-RAR
run_id: valid-minimal
produced_by_task: R-2
touched_by: [R-2, R-3]
sources: [INT-011.A1]
---
# Risk assessment report

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Field Data Relay | C-1 |
| Acronym | FDR | C-1 |
| System ID | FDR-0001 | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | FDR-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: none | C-2 |
| Categorization approved | yes (PER-AO) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-7 | S-1 |
| Classification and handling markings | unclassified; markings: CUI | C-1 |
| IT type | major-application, networked | C-1 |
| Owning organization | Example Program Office | C-1 |
| System version | 1.0 (released 2026-09-01) | C-1 |
| Operational environment | test | C-1 |
| Life-cycle phase | PH-EMD | C-1 |
<!-- END rmf:facts -->

## Risk determination

A low risk remains from the open account-review weakness and a moderate risk from root SSH
login on the appliance; both are covered by POA&M items [[INT-011.A1]] [[ART-POAM]].

## Risk response

Both risks are mitigated; the CAT I item becomes a condition of the authorization
[[INT-037.A1]].
