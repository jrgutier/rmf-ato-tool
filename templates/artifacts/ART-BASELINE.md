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

<<FILL: per provider: what is offered, fully or in part, and its authorization (S-1, from ART-ORG-CONTEXT), with tokens>>

<!-- S-3 adds, per provider, the system owner's and AO's determination (allocation.yaml providers) that it protects the system commensurate with risk. -->

## Tailoring and allocation

<<FILL: summary of artifacts/data/tailoring.yaml (assumptions tested, the assurance determination, overlay conditions, the cost, schedule, performance and other trade-offs weighed, and each remove and compensating action with its law and policy test) and allocation.yaml (the requirements each control satisfies), any capabilities.yaml mapping, and who produced them, with tokens>>

## Privacy tailoring

<<FILL: for a system processing PII, how PER-PRIV took part with PER-ISSM in selecting and tailoring the privacy controls, and that the tailoring leaves no gap in compliance with privacy requirements and adds no privacy risk; or a sentence saying the system processes no PII, with tokens>>

## Requirements to address in tailoring

<<FILL: requirements from ART-REQ the baseline does not obviously cover, or a sentence saying none, with tokens>>
