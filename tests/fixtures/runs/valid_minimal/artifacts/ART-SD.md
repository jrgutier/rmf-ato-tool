---
artifact_id: ART-SD
run_id: valid-minimal
produced_by_task: C-1
touched_by: [C-1, I-2]
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
| Control baseline | CNSSI1253-M-M-L-SUBSET-7 | S-1 |
<!-- END rmf:facts -->

## Users

Operators monitor relay health; administrators manage the appliance [[product/users.md]].

## Leveraged authorizations

Sign-in relies on the separately authorized enterprise identity provider [[INT-003.A1]].

## As built

The developers confirmed the description against the build [[INT-033.A1]].
