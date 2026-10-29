---
artifact_id: ART-RAR
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: R-2
touched_by: [R-2]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Risk assessment report

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-RAR (playbook: playbooks/R/R-2.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Method

<<FILL: how risks were derived from findings and rated (SP 800-30 Table I-2), with tokens>>

## Risks

<<FILL: a narrative per risk rated moderate or higher, named by RSK-### ID, with tokens>>

## Risk determination

<<FILL: the overall risk determination and its comparison with the organizational risk tolerance, with tokens>>

## Recommended responses

<<FILL: the response recommended per risk and any concurrence needed, with tokens>>
