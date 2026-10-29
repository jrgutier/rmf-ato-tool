---
artifact_id: ART-CMP
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: S-4
touched_by: [S-4]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Configuration management plan

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-CMP (playbook: playbooks/S/S-4.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Purpose and scope

<<FILL: what the plan covers, its relation to organizational SecCM policy, and the rigor applied given the categorization in the facts block, with tokens>>

## Roles and responsibilities

<<FILL: SecCM roles: system owner, SecCM program manager, ISSO, system administrators, developers, users and the AO, with persona IDs and duties, with tokens>>

## Configuration control board

<<FILL: membership and chair, meeting cadence and what triggers an emergency meeting, quorum, decision rule, scope of authority and when a change goes to the AO, with tokens>>

## Configuration items and component inventory

<<FILL: the configuration items under control and how they map to the inventory in ART-INV, named by INV-### ID, with tokens>>

## Baseline configurations

<<FILL: the common secure configurations used as the basis, such as DISA STIGs and SRGs, the approved baseline per configuration item, the criteria for approving a baseline, and each deviation with its justification, with tokens>>

## Configuration change control

<<FILL: the change procedure from request through security impact analysis, board decision, testing, implementation, verification and record; pre-approved routine changes; emergency changes and their after-the-fact review, with tokens>>

## Security impact analysis

<<FILL: who performs the analysis, its steps, and the criteria that make a change significant enough to report to the AO, with tokens>>

## Access restrictions for change

<<FILL: who may change configurations and how that is enforced, and how SecCM records are protected, with tokens>>

## Configuration monitoring

<<FILL: how drift and unauthorized changes are detected, how often, with which tools, to whom they are reported and how they are handled, with tokens>>

## Records and tools

<<FILL: where change requests, analyses, approvals and baselines are kept, and the SecCM tools used, with tokens>>

## Plan maintenance and exceptions

<<FILL: who maintains the plan, how often it is reviewed, and how exceptions to it are handled, with tokens>>

<!-- I-2 appends "## Implementation updates" and M-1 appends "## Change updates" (dated:
     what changed in the plan, baselines or board, and why), each adding itself to
     touched_by. -->
