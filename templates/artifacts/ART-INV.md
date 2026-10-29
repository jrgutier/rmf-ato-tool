---
artifact_id: ART-INV
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: P-10
touched_by: [P-10]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Hardware and software inventory

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-INV (playbook: playbooks/P/P-10.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## How the inventory was compiled

<<FILL: sources consulted and who confirmed the items, with tokens>>

## Inventory summary

<<FILL: item counts by kind and by component; name items by INV-### ID; the records live in artifacts/data/inventory.yaml>>

## Asset priority

<<FILL: the asset ranking by mission impact and the reasons, with tokens>>

## Uncertain items

<<FILL: items whose presence or version is unconfirmed and the assumption recorded for each, or a sentence saying none, with tokens>>
