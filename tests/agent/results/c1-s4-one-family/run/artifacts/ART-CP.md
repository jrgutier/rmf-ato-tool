---
artifact_id: ART-CP
run_id: agent-c1-s4-one-family
produced_by_task: S-4
touched_by: [S-4]
sources: [product/conops.md#availability, product/conops.md#environment, product/test-results.md#dt-2]
---
# Contingency plan

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Sensor Gateway | C-1 |
| Acronym | ESG | C-1 |
| System ID | ESG-001 | C-1 |
| Aliases | none | C-1 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-55 | S-1 |
<!-- END rmf:facts -->

## Plan summary

The plan covers the loss of an ESG unit or its site link, which removes perimeter sensing at
that site until service is restored [[product/conops.md#availability]]. The recovery objective
is a replacement unit on site within 72 hours, while the SOC compensates with guard patrols it
can sustain for several days [[product/conops.md#availability]]. IODS flags a site that has been
silent for 5 minutes, which starts the recovery [[product/conops.md#environment]]. During an IODS
outage the local buffer holds up to 7 days of telemetry and replays it oldest first, verified
without loss after a 6-hour outage in DT-2 [[product/test-results.md#dt-2]].
