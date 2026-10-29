---
artifact_id: ART-IRP
run_id: agent-skeleton
produced_by_task: S-4
touched_by: [S-4]
sources: [INT-013.A5, INT-015.A1, product/architecture.md#logging, product/architecture.md#leveraged, ART-ORG-CONTEXT]
---
# Incident response plan

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

This plan covers security incidents on any ESG unit and its sensor network
[[product/architecture.md#logging]]. Detection rests on the events every unit forwards over TLS
to the CSSP SIEM within one minute, where the Installation CSSP correlates and monitors them
[[INT-013.A5]] [[INT-015.A1]]. The ISSO reviews the ESG-specific SIEM report weekly and reports
suspected incidents to the CSSP, which provides incident response support under its ATO of
2026-01-30 [[product/architecture.md#logging]] [[product/architecture.md#leveraged]]
[[ART-ORG-CONTEXT]]. The ISSO coordinates the ESG side with the ISSM and the program office, and
the CSSP leads the installation response. The full plan is later work.
