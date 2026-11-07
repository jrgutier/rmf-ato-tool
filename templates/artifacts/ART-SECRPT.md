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

<<FILL: the period covered, the marking, and the recipients and frequency from ART-CONMON, with the DoD bodies this system's GENSER or SE designation adds; the records live in artifacts/data/posture-reports.yaml; with tokens>>

## Posture summary

<<FILL: the current security and privacy posture: control effectiveness from ongoing assessments and monitoring, with tokens>>

## Changes since the last report

<<FILL: changes to the security plan, assessment results and POA&M since the last report, named by ID, with tokens>>

## Risks and planned responses

<<FILL: new or changed risks found by assessment, auditing or monitoring, and how the system owner or provider plans to address them, with tokens>>

## Matters for ongoing authorization

<<FILL: triggers reached and items the AO needs for the ongoing authorization decision, or a sentence saying none, with tokens>>

## Status to DoD bodies

<<FILL: what reached each body in the period (POA&M updates, inspection findings, vulnerability and risk acceptance status, external service status changes, scorecard and CMRS statistics) and how the data is shared, with tokens>>

## Privacy reporting

<<FILL: for a system processing PII, the Component's privacy report path: the PCLO through the SCOP to the Chief, DPCLTD, the semiannual Section 803 and FISMA privacy inputs this system feeds, and any system of records with PII that cannot be appropriately protected, made known to the DoD SAOP; or a sentence saying the system processes no PII, with tokens>>

## Organization tier review

<<FILL: the review of these reports by the risk executive (function) and the CISO, the aggregate POA&M position and what it feeds into the organizational strategy at P-7, with tokens>>
