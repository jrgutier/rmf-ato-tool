---
artifact_id: ART-REQ
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: P-15
touched_by: [P-15]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Security and privacy requirements and allocation

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-REQ (playbook: playbooks/P/P-15.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Sources of requirements

<<FILL: the laws, policies, capability requirements, stakeholder needs and risk assessment results the requirements come from, with tokens>>

## Security and privacy requirements

<<FILL: table: REQ-## ID | requirement | source | priority, one testable requirement per row, with tokens>>

## Operational constraints

<<FILL: mission and operational constraints the requirements must respect, from the user representative and sponsor, with tokens>>

<!-- P-17 adds an "Allocated to" column (component IDs from artifacts/data/boundary.yaml, or
     the environment of operation) to the requirements table, appends "## Allocation" (how
     each requirement is split between the system, its elements and providers, and why), and
     adds P-17 to touched_by. -->
