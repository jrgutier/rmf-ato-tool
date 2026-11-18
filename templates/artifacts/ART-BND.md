---
artifact_id: ART-BND
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: P-11
touched_by: [P-11]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Authorization boundary, network architecture and data flows

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-BND (playbook: playbooks/P/P-11.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Authorization boundary

<<FILL: what is inside, what is outside and why, where the edge is, with tokens>>

## Network architecture

<<FILL: networks, interfaces and permitted traffic, with tokens>>

## Data flows

<<FILL: each flow across or inside the boundary and its protection, and which flows carry PII and of which information types (boundary.yaml data_flow carries_pii and pii_types), with tokens>>

## External components

<<FILL: each external system or service, how it is authorized, and (after C-1) its leveraged authorization, with tokens>>

<!-- P-16 appends "## Enterprise Architecture (P-16)" (the heading its playbook names) with
     "### Connections and approvals": each external connection of artifacts/data/boundary.yaml
     (keys `connections`, `dodin`, `hosting`) by CONN ID, the approvals and agreement it needs
     and their status, any cross-domain solution and mission partner terms, and whether the
     system is on the DODIN or outside it under a waiver; it adds P-16 to touched_by. -->
