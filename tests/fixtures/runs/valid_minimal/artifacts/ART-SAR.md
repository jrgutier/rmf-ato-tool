---
artifact_id: ART-SAR
run_id: valid-minimal
produced_by_task: A-3
touched_by: [A-3, A-4, A-5]
sources: [INT-009.A1]
handling: CUI
---
# Security assessment report

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

## Assessment summary

The assessment covered the controls of the subset; the most significant finding is the root SSH
login [[INT-009.A1]].

## Results

Four controls are satisfied and SC-15 is not applicable. AC-2 is other than satisfied because no quarterly account
review has been performed yet (FND-001), and CM-6 because the image permits root SSH login
(FND-002) [[INT-009.A1]] [[INT-009.A2]].

## Report

The assessor delivered the report to the AO and the program manager [[INT-035.A1]].

## Remediation

Console audit forwarding (FND-003) was fixed and re-tested during the assessment
[[INT-036.A1]].
