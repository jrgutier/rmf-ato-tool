---
artifact_id: ART-BIA
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: P-8
touched_by: [P-8]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Business impact and criticality analysis

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-BIA (playbook: playbooks/P/P-8.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment.
     The record is artifacts/data/bia.yaml; this document explains it. C-2 adds the reevaluations
     and then lists itself in touched_by. -->

## Mission critical functions

<<FILL: whether mission critical functions are present within the system, and if so each one and the processes that carry it, with tokens>>

## Supported processes and disruption impact

<<FILL: table: process | impact of disruption (low, moderate, high) | users' recovery time requirement | interdependencies, with tokens>>

## External dependents

<<FILL: the external stakeholders that depend on the system's critical functions or processes and how that is communicated to them, or a sentence saying none, with tokens>>

## Reevaluations

<<FILL: at C-2, each process whose disruption impact exceeds the availability impact of the categorization, reevaluated by the mission owner and the data owner, and the outcome; or a sentence saying none conflicts, with tokens>>
