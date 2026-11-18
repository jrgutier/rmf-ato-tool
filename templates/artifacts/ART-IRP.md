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

<<FILL: what counts as an event and an incident for this system, the risk factors behind triage and escalation, categorization by type, containment and eradication criteria, the incident lead, how third parties report, the fields tracked per incident and evidence handling (`triage` in artifacts/data/incident-response.yaml), with tokens>>

## Roles, responsibilities and authorities

<<FILL: who handles incidents on the system team, leadership, legal, public affairs and the privacy officer, and who has authority to disconnect or shut down components, with persona IDs, with tokens>>

## Shared responsibility with the CSSP and providers

<<FILL: what the cybersecurity service provider and other providers do and what the system team does, the information flows between them, and each party's authority to act, with tokens>>

## Detection and analysis

<<FILL: the sources that detect incidents, such as logs forwarded to the CSSP, alerts and user reports; how up-to-date cyber threat intelligence is used in log analysis, to correlate events across log sources and in adverse event analysis (artifacts/data/incident-response.yaml detection); and how a possible incident is analyzed and confirmed, with tokens>>

## Response and reporting

<<FILL: the reporting path of each case in `reporting_paths` (CSSP, JFHQ-DODIN, chain of command, classified compromise, CUI, law enforcement) with timelines, containment and eradication, and who is told what and when under the laws and agreements that apply: asset owners, senior leadership, human resources, third parties, the media and the public, and PII breaches through the privacy officer (`notifications` in artifacts/data/incident-response.yaml), with tokens>>

## Recovery

<<FILL: the criteria that start and end recovery, how actions are chosen and reassessed, integrity checks on restoration assets and restored systems, who is told, restoring affected components and data in coordination with ART-CP, and monitoring after restoration (`recovery` in artifacts/data/incident-response.yaml), with tokens>>

## Lessons learned

<<FILL: how lessons from incidents and exercises are captured and fed back into the plan and the system, with tokens>>

## Training, testing and plan maintenance

<<FILL: training for the people named in the plan, how often the plan is tested, the performance measures used, and who maintains it, with tokens>>

<!-- I-2 appends "## Update Control Implementation Information (I-2)" (dated: what changed during implementation and
     why) and adds I-2 to touched_by. -->
