---
artifact_id: ART-CMP
run_id: agent-cold-start-resume
produced_by_task: S-4
touched_by: [S-4]
sources: [INT-014.A1, INT-016.A1, product/architecture.md#configuration, product/architecture.md#updates]
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
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-6 | S-1 |
<!-- END rmf:facts -->

## Plan summary

This plan covers the configuration of every ESG unit: the gateway OS, collector, console and
buffer database, which all run one shared baseline [[product/architecture.md#configuration]].
The baseline is a signed OS image the developer's pipeline hardens from the applicable DISA
SRGs and STIGs, recording each deviation [[INT-014.A1]]. The RSSPO configuration control board
approves every baseline change and every deviation, including each monthly update bundle
[[INT-016.A1]]. A nightly configuration check on each unit reports drift from the approved
baseline to the CSSP SIEM, where the ISSO follows it up [[INT-014.A1]].
