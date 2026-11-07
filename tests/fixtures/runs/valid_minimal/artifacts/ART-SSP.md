---
artifact_id: ART-SSP
run_id: valid-minimal
produced_by_task: S-4
touched_by: [S-4, S-6, I-2, A-5]
sources: [INT-007.A1, ART-BASELINE]
---
# System security plan

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

## Approach

Control statements live in artifacts/ssp/controls; each cites the interview or product
passage it rests on [[INT-007.A1]] [[ART-BASELINE]].

## Approval

The AODR approved the SSP for assessment [[INT-031.A1]].

## As built

Statements were confirmed against the build [[INT-033.A1]].

## After remediation

Console audit forwarding was fixed during testing; the AU-2 statement stands
[[INT-036.A1]].
