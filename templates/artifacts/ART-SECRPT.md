---
artifact_id: ART-SECRPT
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: M-5
touched_by: [M-5]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Security and privacy posture report

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-SECRPT (playbook: playbooks/M/M-5.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Reporting period and recipients

<<FILL: the period covered, the recipients and the reporting frequency from ART-CONMON, with tokens>>

## Posture summary

<<FILL: the current security and privacy posture: control effectiveness from ongoing assessments and monitoring, with tokens>>

## Changes since the last report

<<FILL: changes to the security plan, assessment results and POA&M since the last report, named by ID, with tokens>>

## Risks and planned responses

<<FILL: new or changed risks found by assessment, auditing or monitoring, and how the system owner or provider plans to address them, with tokens>>

## Matters for ongoing authorization

<<FILL: triggers reached and items the AO needs for the ongoing authorization decision, or a sentence saying none, with tokens>>
