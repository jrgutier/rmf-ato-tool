---
artifact_id: ART-IRP
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: S-4
touched_by: [S-4]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Incident response plan

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-IRP (playbook: playbooks/S/S-4.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Purpose and scope

<<FILL: management commitment, the plan's objectives, and what and whom it covers, with tokens>>

## Definitions and prioritization

<<FILL: what counts as an event and an incident for this system, and how incidents are prioritized and their severity estimated, with tokens>>

## Roles, responsibilities and authorities

<<FILL: who handles incidents on the system team, leadership, legal, public affairs and the privacy officer, and who has authority to disconnect or shut down components, with persona IDs, with tokens>>

## Shared responsibility with the CSSP and providers

<<FILL: what the cybersecurity service provider and other providers do and what the system team does, the information flows between them, and each party's authority to act, with tokens>>

## Detection and analysis

<<FILL: the sources that detect incidents, such as logs forwarded to the CSSP, alerts and user reports, and how a possible incident is analyzed and confirmed, with tokens>>

## Response and reporting

<<FILL: reporting to the CSSP and the chain of command with timelines, containment and eradication, evidence handling, and notifications including PII breaches through the privacy officer, with tokens>>

## Recovery

<<FILL: restoring affected components and data, in coordination with ART-CP, and confirming normal operation, with tokens>>

## Lessons learned

<<FILL: how lessons from incidents and exercises are captured and fed back into the plan and the system, with tokens>>

## Training, testing and plan maintenance

<<FILL: training for the people named in the plan, how often the plan is tested, the performance measures used, and who maintains it, with tokens>>

<!-- I-2 appends "## Implementation updates" (dated: what changed during implementation and
     why) and adds I-2 to touched_by. -->
