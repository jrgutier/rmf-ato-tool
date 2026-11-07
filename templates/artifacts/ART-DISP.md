---
artifact_id: ART-DISP
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: M-7
touched_by: [M-7]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Disposal plan

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-DISP (playbook: playbooks/M/M-7.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Disposal strategy

<<FILL: how and when the system is disposed of, the secure end state, whether the environment returns to its original secure state or one set by agreement, and the storage criteria if the system is stored first, as in artifacts/data/disposal.yaml, with tokens>>

## Information disposition

<<FILL: for each information type, named by INF-## ID: retained, transferred or destroyed, under which record retention rules, with tokens>>

## Media sanitization and component disposal

<<FILL: how each inventory item, named by INV-### ID, is sanitized or destroyed and how that is verified and recorded, with tokens>>

## Users, interconnections and inheritance

<<FILL: users and hosted applications notified, interconnections ended, and inheritance relationships reviewed for impact, with tokens>>

## Records and registry updates

<<FILL: updates to the inventory, the security plan, the Component registry and the final posture report, and the end of the authorization, with tokens>>
