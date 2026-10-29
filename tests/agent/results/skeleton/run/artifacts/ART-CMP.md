---
artifact_id: ART-CMP
run_id: agent-skeleton
produced_by_task: S-4
touched_by: [S-4]
sources: [INT-014.A1, INT-014.A2, INT-019.A2, product/architecture.md#configuration, ART-ORG-CONTEXT]
---
# Configuration management plan

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

This plan covers the configuration of every ESG unit: the gateway OS, collector, console and
buffer database [[product/architecture.md#configuration]]. The baseline is one signed OS image
that the developer's pipeline builds and hardens to the applicable DISA SRGs and STIGs, recording
every deviation [[INT-014.A1]] [[ART-ORG-CONTEXT]]. The RSSPO configuration control board approves
deviations and every change to the baseline, including firewall rules and each monthly update
bundle [[INT-014.A2]] [[INT-019.A2]]. A configuration check runs nightly on each unit and reports
drift from the approved baseline to the CSSP SIEM [[INT-014.A2]]. The full plan is later work.
