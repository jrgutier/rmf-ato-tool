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

<<FILL: the plan's name and type, its purpose, the policy it rests on (`policy`), what it covers with the availability impact in the facts block, its assumptions, the situations it does not cover, and how it is coordinated with the related plans of `scope.related_plans` in artifacts/data/contingency.yaml, with tokens>>

## Concept of operations

<<FILL: the parts of the system the plan restores, pointing to ART-SD and ART-BND, and the three plan phases: activation and notification, recovery, reconstitution, with tokens>>

## Business impact analysis

<<FILL: the analysis behind `bia` in artifacts/data/contingency.yaml: the mission processes, the resources needed and their interdependencies, the impact categories and severity scale, the points of contact consulted, and the optimum point balancing the cost of an outage against the cost of recovery, with tokens>>

## Preventive controls

<<FILL: the platform measures of `preventive` in artifacts/data/contingency.yaml: UPS, generators, fire and water protection, failover and redundancy, with tokens>>

## Recovery strategy

<<FILL: why this strategy fits the system: the alternatives compared, the BIA impacts and downtimes it answers, the availability impact level, the offsite store and alternate site and the agreements behind them, the backup solution, equipment needs, the budget case, and each process whose RTO cannot be met (`strategy`, `sites`, `backup` in artifacts/data/contingency.yaml), with tokens>>

## Roles and responsibilities

<<FILL: the contingency plan coordinator, recovery teams staffed by skill and their leads and alternates, the one activating authority and its successor, and the vendor contacts, service agreements and equipment commitments of `teams` in artifacts/data/contingency.yaml, with persona IDs, with tokens>>

## Activation and notification

<<FILL: activation criteria and who may activate the plan, notification for each case and when a person cannot be reached, what each message says, and the outage assessment's minimum areas (`activation`), with tokens>>

## Recovery

<<FILL: the sequence of recovery activities tied to the BIA priorities and the MTD, step-by-step procedures by component and team, shipment to an alternate site, and escalation triggers and notices (`recovery`), with tokens>>

## Reconstitution

<<FILL: concurrent processing, validation that the system works and its data is complete, return to normal operations, notifications, cleanup, return of offsite media, fresh backups, the significant change determination, documentation and plan deactivation (`reconstitution`), with tokens>>

## Testing, training and exercises

<<FILL: the test plan of `exercises` and `testing` in artifacts/data/contingency.yaml: objectives, success criteria, schedule, participants, scope, scenario and logistics; the exercise type for the availability level; the event under realistic cyber conditions and the evaluation of operating with all information resources and connectivity lost; what training covers (`training`); and the results of the latest test, with tokens>>

## Plan maintenance

<<FILL: who maintains the plan, the minimum review elements, the record of changes and of copies, marking, version control, coordination on change, what triggers an update, and upkeep through disposal (`maintenance`), with tokens>>

## Appendices

<<FILL: the contact list, diagrams, inventory, interconnections and constraints of `appendices` in artifacts/data/contingency.yaml, or where each is kept, with tokens>>

<!-- I-2 appends "## Update Control Implementation Information (I-2)" (dated: what changed during implementation and
     why) and adds I-2 to touched_by. -->
