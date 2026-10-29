---
artifact_id: ART-SAR
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: A-3
touched_by: [A-3]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Security assessment report

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-SAR (playbook: playbooks/A/A-3.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Assessment summary

<<FILL: what was assessed, how, and the result mix; results live in artifacts/sar/results/FAM.yaml; with tokens>>

## Test results reused

<<FILL: which test events were reused and what they showed, with tokens>>

## Findings overview

<<FILL: the most significant findings by FND-### ID, with severity and evidence, with tokens>>

## Recommendations

<<FILL: recommended remediation per significant finding, with tokens>>
