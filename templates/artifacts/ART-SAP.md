---
artifact_id: ART-SAP
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: A-2
touched_by: [A-2]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Security assessment plan

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-SAP (playbook: playbooks/A/A-2.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Scope and objectives

<<FILL: the tailored baseline in scope, exclusions with rationale, objectives, with tokens>>

## Approach and methods

<<FILL: examine, interview and test, depth and coverage, with tokens>>

## Reuse of test results

<<FILL: which developer or developmental test results are reused and why they are sound, with tokens>>

## Team and independence

<<FILL: assessors, roles and independence, with tokens>>

## Schedule

<<FILL: start, end and events; the dates live in artifacts/data/sap.yaml; with tokens>>

## Rules of engagement

<<FILL: what assessors may do, where, when, and who is notified, with tokens>>

## Review and approval

<<FILL: who reviewed, findings, and the AO's approval, with tokens>>
