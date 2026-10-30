---
artifact_id: ART-CP
run_id: agent-cold-start-resume
produced_by_task: S-4
touched_by: [S-4]
sources: [product/conops.md#availability, product/conops.md#environment, product/architecture.md#components, product/test-results.md#dt-2]
---
# Contingency plan

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

## Plan summary

This plan covers the loss of one ESG unit or its site link, which removes perimeter sensing at
that site until service is restored [[product/conops.md#availability]]. The recovery objective
is a replacement unit on site within 72 hours, while the SOC covers the site with guard patrols,
which it can sustain for several days [[product/conops.md#availability]]. IODS flags a site
silent for 5 minutes, which starts the plan [[product/conops.md#environment]]. While IODS is
unreachable, the local buffer keeps up to 7 days of telemetry and replays it oldest first,
as the 6-hour outage test showed [[product/architecture.md#components]] [[product/test-results.md#dt-2]].
