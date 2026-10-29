---
artifact_id: ART-CAT
run_id: valid-minimal
produced_by_task: C-2
touched_by: [C-2, C-3]
sources: [INT-004.A1, ART-INFOTYPES]
---
# Security categorization

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
<!-- END rmf:facts -->

## Basis

Sensor reports drive moderate confidentiality and integrity; availability is low because
field units buffer reports [[INT-004.A1]] [[ART-INFOTYPES]].

## Approval

The AODR approved the categorization for the AO [[INT-005.A1]].
