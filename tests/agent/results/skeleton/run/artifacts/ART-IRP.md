---
artifact_id: ART-IRP
run_id: agent-skeleton
produced_by_task: S-4
touched_by: [S-4]
sources: [INT-013.A3, INT-012.A1, product/architecture.md#logging, product/architecture.md#leveraged]
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
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-6 | S-1 |
<!-- END rmf:facts -->

## Plan summary

This plan covers security incidents on any ESG unit and relies on the Installation CSSP, which
provides monitoring and incident response support under its own authorization
[[product/architecture.md#leveraged]]. Detection rests on the agreed audit events, which every
unit forwards to the CSSP SIEM within one minute for correlation [[INT-013.A3]]
[[INT-012.A1]]. The ISSO reviews the ESG report weekly and reports a suspected incident to the
CSSP, which leads the response with the ISSO and the developer [[INT-013.A3]]
[[product/architecture.md#logging]]. Until release 2.3, events from the shared `fieldtech`
account identify the account, not the technician, which limits attribution in an
investigation [[INT-013.A3]].
