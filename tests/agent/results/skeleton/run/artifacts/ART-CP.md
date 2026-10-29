---
artifact_id: ART-CP
run_id: agent-skeleton
produced_by_task: S-4
touched_by: [S-4]
sources: [product/conops.md#availability, product/architecture.md#components, product/test-results.md#dt-2, product/conops.md#environment]
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
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: none | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | SP800-53B-MODERATE-SUBSET-6 | S-1 |
<!-- END rmf:facts -->

## Plan summary

This plan covers the loss of an ESG unit or of its link to IODS at one site
[[product/conops.md#availability]]. The recovery objective is the program's stated goal of a
replacement unit on site within 72 hours, while the SOC covers the site with guard patrols, which
it can sustain for several days [[product/conops.md#availability]]. When IODS is unreachable, the
local buffer holds up to 7 days of telemetry and replays it oldest first, which DT-2 showed
without loss after a 6-hour outage [[product/architecture.md#components]]
[[product/test-results.md#dt-2]]. IODS flags a site that has been silent for 5 minutes, which
starts the recovery [[product/conops.md#environment]]. The full plan is later work.
