---
artifact_id: ART-BASELINE
run_id: valid-minimal
produced_by_task: S-1
touched_by: [S-1, S-2, S-3]
sources: [INT-006.A1]
---
# Control baseline

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

## Selection

The CNSSI 1253 per-objective selection for the approved categorization applies, restricted
to the seven controls of the fixture profile, with a quarterly account review parameter
[[INT-006.A1]] [[ART-CAT]].

## Tailoring

The account review frequency is set to quarterly; nothing else is tailored [[INT-028.A1]].

## Allocation

Boundary protection is inherited from the enclave, identity is shared with the identity
provider and the remaining controls are system-specific [[INT-029.A1]].
