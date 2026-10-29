---
artifact_id: ART-SSP
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: S-4
touched_by: [S-4]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# System security plan

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-SSP (playbook: playbooks/S/S-4.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Approach to control implementation

<<FILL: how the controls are implemented across the components, with tokens; the statements live in artifacts/ssp/controls/FAM.yaml>>

## Inheritance and shared responsibility

<<FILL: one paragraph per provider: what it implements and what the system does, with tokens>>

## Open items

<<FILL: each partial or planned control with its gap and plan, named by control ID, with tokens>>
