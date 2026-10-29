---
artifact_id: ART-BASELINE
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: S-1
touched_by: [S-1]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Control baseline, tailoring and allocation

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-BASELINE (playbook: playbooks/S/S-1.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Selection basis

<<FILL: the selection method recorded in baseline.json (CNSSI 1253 per-objective selection plus the NSS privacy control baseline, or the SP 800-53B high-water mark when CNSSI 1253 is degraded) for the approved categorization in the facts block, and the overlays applied, with tokens>>

## Common controls available for inheritance

<<FILL: per provider: what is offered, fully or in part, and its authorization, with tokens>>

## Tailoring and allocation

<<FILL: summary of artifacts/data/tailoring.yaml and allocation.yaml and who produced them, with tokens>>

## Requirements to address in tailoring

<<FILL: requirements from ART-REQ the baseline does not obviously cover, or a sentence saying none, with tokens>>
