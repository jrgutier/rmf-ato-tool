---
artifact_id: ART-CP
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: S-4
touched_by: [S-4]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Contingency plan

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-CP (playbook: playbooks/S/S-4.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Introduction and scope

<<FILL: the plan's purpose, what it covers with the availability impact in the facts block, its assumptions, and the situations it does not cover, with tokens>>

## Concept of operations

<<FILL: the parts of the system the plan restores, pointing to ART-SD and ART-BND, and the three plan phases: activation and notification, recovery, reconstitution, with tokens>>

## Business impact analysis

<<FILL: the mission processes the system supports, their maximum tolerable downtime, the recovery time and recovery point objectives, and the recovery priority of each component, with tokens>>

## Preventive controls

<<FILL: measures that reduce the effect of a disruption, such as backups, power protection and redundancy, with tokens>>

## Recovery strategy

<<FILL: backup and recovery approach, backup methods and offsite storage, alternate site or spare equipment, and equipment replacement, with tokens>>

## Roles and responsibilities

<<FILL: the contingency plan coordinator, recovery teams and their leads, and how to reach them, with persona IDs, with tokens>>

## Activation and notification

<<FILL: activation criteria and who may activate the plan, notification procedures and the outage assessment, with tokens>>

## Recovery

<<FILL: the sequence of recovery activities, recovery procedures by component, and escalation and notification during recovery, with tokens>>

## Reconstitution

<<FILL: validation that the system works and its data is complete, return to normal operations, notifications, cleanup, fresh backups, documentation and plan deactivation, with tokens>>

## Testing, training and exercises

<<FILL: how and how often the plan is tested and exercised and personnel trained, and the results of the latest test, with tokens>>

## Plan maintenance

<<FILL: who maintains the plan, how often it is reviewed, and what triggers an update, with tokens>>

<!-- I-2 appends "## Implementation updates" (dated: what changed during implementation and
     why) and adds I-2 to touched_by. -->
