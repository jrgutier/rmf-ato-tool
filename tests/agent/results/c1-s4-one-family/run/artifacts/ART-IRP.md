---
artifact_id: ART-IRP
run_id: agent-c1-s4-one-family
produced_by_task: S-4
touched_by: [S-4]
sources: [product/architecture.md#logging, INT-015.A2, INT-013.A3]
---
# Incident response plan

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

The plan covers security incidents on any ESG unit and its sensor network. Detection rests on
the security-relevant events ESG forwards to the CSSP SIEM within one minute, which the CSSP
correlates and alerts on [[product/architecture.md#logging]] [[INT-015.A2]]. The CSSP leads
incident response for the installation, and the ESG ISSO is the system's point of contact who
receives its alerts and reviews the weekly ESG report [[INT-013.A3]]. The ISSO reports suspected
incidents to the CSSP and supports its handling with the locally held 30 days of logs
[[product/architecture.md#logging]].
