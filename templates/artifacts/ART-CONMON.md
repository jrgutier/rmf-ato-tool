---
artifact_id: ART-CONMON
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: S-5
touched_by: [S-5]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Continuous monitoring strategy

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-CONMON (playbook: playbooks/S/S-5.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Strategy overview

<<FILL: how the system strategy implements the organizational continuous monitoring strategy in ART-ORG-CONTEXT and supports ongoing authorization, with tokens>>

## Monitoring frequencies

<<FILL: per control family, how often and by what method effectiveness is monitored and who does it; the records live in artifacts/data/conmon.yaml; with tokens>>

## Ongoing authorization triggers

<<FILL: the time-driven trigger in days and each event that triggers a review of the authorization, as in conmon.yaml ongoing_authorization, with tokens>>

## Reporting

<<FILL: who receives posture reports, how often and in what form, as in conmon.yaml reporting, with tokens>>

## Roles and tools

<<FILL: who collects, analyzes and reports monitoring data, including the CSSP and common control providers, and the tools used; which asset classes detection covers at all times (networks, the physical environment, personnel activity, external providers, computing) and how monitoring is tuned against false positives and negatives, as in conmon.yaml detection_coverage and tuning, with tokens>>

<!-- M-2 updates artifacts/data/conmon.yaml when ongoing assessments change a frequency or
     method, appends "## Changes after ongoing assessment" (what changed and why), and adds
     M-2 to touched_by. -->
