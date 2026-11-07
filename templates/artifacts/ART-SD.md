---
artifact_id: ART-SD
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: C-1
touched_by: [C-1]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# System description

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-SD (playbook: playbooks/C/C-1.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Mission and purpose

<<FILL: the mission the system supports and what it does, with tokens>>

## System description and functions

<<FILL: components, functions and how the system works end to end, with tokens>>

## Users

<<FILL: user groups, their access and privileges; records live in artifacts/data/users.yaml; with tokens>>

## Operating environment

<<FILL: sites, physical setting and supporting infrastructure, with tokens>>

## Interconnections and leveraged authorizations

<<FILL: interconnected systems and agreements; leveraged authorizations (LA-##) from artifacts/data/leveraged-authorizations.yaml; the Receiving organizations, received systems and reciprocity agreements of artifacts/data/reciprocity.yaml; with tokens>>
