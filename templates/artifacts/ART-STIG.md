---
artifact_id: ART-STIG
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: I-1
touched_by: [I-1]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# STIG and SRG summary

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-STIG (playbook: playbooks/I/I-1.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Applicability

<<FILL: which STIGs and SRGs apply to which inventory items, named by BM-## and INV-### ID, and the items with no applicable benchmark and why; the records live in artifacts/data/stig-summary.yaml; with tokens>>

## Scan results

<<FILL: scan dates and tools, naming the tool from `tools` in artifacts/data/cm-plan.yaml, and finding counts by category and status, with tokens>>

## Open findings

<<FILL: the open findings, CAT I first, named by STG-### ID with the related control and the planned fix, with tokens>>

## Accepted deviations

<<FILL: deviations from a benchmark approved through configuration management, with the approval and justification, or a sentence saying none, with tokens>>

<!-- A-3 appends "## Assessor verification" (which results the assessor verified, how, and
     any status corrected in artifacts/data/stig-summary.yaml) and adds A-3 to touched_by. -->
