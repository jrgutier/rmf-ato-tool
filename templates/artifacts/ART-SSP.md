---
artifact_id: ART-SSP
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: S-4
touched_by: [S-4]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# System security plan

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-SSP (playbook: playbooks/S/S-4.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Approach to control implementation

<<FILL: how the controls are implemented across the components, and why the security, privacy and C-SCRM plans are consolidated or separate as `plan_structure` in artifacts/data/ssp-records.yaml records, with tokens; the statements live in artifacts/ssp/controls/FAM.yaml>>

## Privacy plan

<<FILL: for a system processing PII, the privacy plan this plan holds with the security plan: an overview of the privacy requirements, the methodologies and metrics that assess the privacy controls, and the PIA it references (ssp-records.yaml privacy_plan; PRIV-008); or a sentence saying the system processes no PII, with tokens>>

## Inheritance and shared responsibility

<<FILL: one paragraph per provider: what it implements and what the system does, with tokens>>

## Plan records

<<FILL: what artifacts/data/ssp-records.yaml holds and why: the funding of control implementation, assessment and sustainment, the cryptography and who approved it, whether non-government equipment reaches the system, and the E-Authentication assessment, with tokens>>

## Open items

<<FILL: each partial or planned control with its gap and plan, named by control ID, with tokens>>
