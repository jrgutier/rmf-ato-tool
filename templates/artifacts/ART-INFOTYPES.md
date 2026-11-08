---
artifact_id: ART-INFOTYPES
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: P-12
touched_by: [P-12]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Information types and information life cycle

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-INFOTYPES (playbook: playbooks/P/P-12.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Information types

<<FILL: table: INF-## ID | information type | SP 800-60 identifier | provisional C, I and A | adjustment and its reason; the records live in artifacts/data/infotypes.yaml; with tokens>>

## Privacy

<<FILL: which information types contain PII and about whom (pii.subjects), whether any holds PHI or SSNs, or a sentence saying none and what was checked; for a system with PII, the issuances its handling complies with (DoD 5400.11-R, DoDI 5400.16, DoD 8580.02-R for PHI), its SORN, the SSN justification, the records office and schedule, and the PIA determination with its DoDI 5400.16 basis and due date (infotypes.yaml privacy; PRIV-001), with tokens>>

## Information owners

<<FILL: the owner or steward of each information type, named by INF-## ID, persona and organization as in infotypes.yaml information_owners, each interviewed, and the answer in which each sets its types' impact levels, with tokens>>

<!-- P-13 appends "## Information life cycle" here (for each information type, the stages it
     passes through from creation to disposition and the components at each stage; the
     life_cycle records go in artifacts/data/infotypes.yaml) and adds P-13 to touched_by. -->
