---
artifact_id: ART-CHG
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: M-1
touched_by: [M-1]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Change log and security impact analyses

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-CHG (playbook: playbooks/M/M-1.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Monitoring scope and sources

<<FILL: the period covered, what was monitored under ART-CONMON, and the sources used, such as change requests, scans and threat information, with tokens>>

## Change log

<<FILL: table: change request reference | date | change | requested by | security impact result | board decision | referred to the AO or not, with tokens>>

## Security impact analyses

<<FILL: for each change with a security impact: what changed, the vulnerabilities and risk it introduced, the controls affected and the mitigation, with tokens>>

## Changes in the environment of operation

<<FILL: changes in threat, mission, interconnections or operating environment that affect the system's risk, or a sentence saying none, with tokens>>

## Resulting updates

<<FILL: the artifacts updated because of these changes (SSP, POA&M, SAR, inventory, CMP) and whether any change needs a reauthorization decision, with tokens>>
