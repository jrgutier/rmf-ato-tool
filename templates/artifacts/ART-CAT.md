---
artifact_id: ART-CAT
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: C-2
touched_by: [C-2]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Security categorization

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-CAT (playbook: playbooks/C/C-2.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Impact per information type

<<FILL: table: information type ID and title | C | I | A | basis for each value ([[INT-###.A#]] or [[ART-INFOTYPES]])>>

## System categorization

<<FILL: how the system values follow from the table (high-water mark per objective), referring to the facts block rather than restating the values, with tokens>>

## Overlays

<<FILL: one line per CNSSI 1253 overlay considered: applies or not, and why, with tokens. For the Privacy Overlays, name the privacy risk level that chose the set and say it is used in place of a PII confidentiality impact level (PCIL), as the overlay's section 4.2 directs although CNSSI 1253 footnote 23 still names PII impact levels>>

<!-- C-3 appends a "## Review and approval" section here and adds C-3 to touched_by. -->
