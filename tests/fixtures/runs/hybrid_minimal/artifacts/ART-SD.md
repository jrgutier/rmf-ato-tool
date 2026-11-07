---
artifact_id: ART-SD
run_id: hybrid-minimal
produced_by_task: C-1
touched_by: [C-1]
sources: [INT-003.A1, product/architecture.md]
---
# System description

The Field Data Relay collects signed sensor reports from field units and relays them to the
analysis enclave [[INT-003.A1]] [[product/architecture.md#overview]].

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
| Control baseline | CNSSI1253-M-M-L-SUBSET-6 | S-1 |
| Classification and handling markings | unclassified; markings: CUI | C-1 |
| IT type | major-application, networked | C-1 |
| Owning organization | Example Program Office | C-1 |
| System version | 1.0 (released 2026-09-01) | C-1 |
| Operational environment | test | C-1 |
| Life-cycle phase | PH-EMD | C-1 |
<!-- END rmf:facts -->

## Users

Operators monitor relay health; administrators manage the appliance [[product/users.md]].

## Interconnections and leveraged authorizations

The relay has no interconnection with another system; sign-in relies on the separately
authorized enterprise identity provider [[INT-003.A1]].
