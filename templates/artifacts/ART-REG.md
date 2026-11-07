---
artifact_id: ART-REG
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: P-18
touched_by: [P-18]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# System registration

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-REG (playbook: playbooks/P/P-18.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Registry and registration record

<<FILL: the Component registry used, the date of registration and the registry's record reference; the system's identifiers live in facts.yaml; with tokens>>

## Registered characteristics

<<FILL: what was registered: purpose, owner, boundary reference and life-cycle state as recorded in the registry, without restating facts, with tokens>>

## Ports, protocols and services

<<FILL: the system's registration in the DoD Ports, Protocols, and Services Management (PPSM) Registry, its number and the boundary connections it covers, as in registration.yaml ppsm; an Enterprise system registers every connection (PPSM-001), with tokens>>

## Registration updates owed

<<FILL: when the record must be updated: after categorization, at the authorization decision (R-5) and at disposal (M-7), and who updates it, with tokens>>
