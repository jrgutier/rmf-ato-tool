---
artifact_id: ART-SVCA
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: S-4
touched_by: [S-4]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Cybersecurity service agreements

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-SVCA (playbook: playbooks/S/S-4.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. M-2 adds itself to
     touched_by with its first measurement. Delete this comment. -->

## Agreements

<<FILL: who provides what under which instrument, as artifacts/data/service-agreements.yaml records, and how the owner of the system checked each agreement, with tokens>>

## Cloud service offering

<<FILL: a cloud-hosted system only (else a sentence saying none): how each offering is securely connected per the Cloud Computing SRG, the cybersecurity T&E in emulated and live environments before operational use, and how audit and log records are determined and reviewed per its reference architecture, with tokens>>

## Effectiveness

<<FILL: how each service is measured, and any issue the provider and subscriber could not resolve, or a sentence saying no measurement is due yet, with tokens>>
