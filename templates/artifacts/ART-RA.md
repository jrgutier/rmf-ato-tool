---
artifact_id: ART-RA
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: P-14
touched_by: [P-14]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# System risk assessment

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-RA (playbook: playbooks/P/P-14.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. The ratings, IDs and
     lists live in artifacts/data/ra.yaml (templates/data/ra.yaml, SRA-001 to SRA-003); this prose
     explains them and never restates a rating differently. Delete this comment. -->

## Method and scope

<<FILL: the purpose and the decisions it supports, initial or subsequent, the scope and its time frame, the assumptions and constraints, the risk model, assessment and analysis approach and why (or where the risk management strategy defines them), the scales and how values combine, the risk tolerance, and the information sources with their dates and the credentialed professionals consulted (ra.yaml purpose to consultations), with tokens>>

## Threat sources and events

<<FILL: table: TE-# | threat event | threat source | likelihood of initiation | likelihood of adverse impact | overall likelihood | impact | risk, and the threat sources with their capability, intent and targeting or range of effects, relevance and threat scenarios, as in ra.yaml, with tokens>>

## Vulnerabilities and predisposing conditions

<<FILL: weaknesses with their severity and predisposing conditions with their pervasiveness, and the threat events each bears on (ra.yaml vulnerabilities and predisposing_conditions), with tokens>>

## Mitigating conditions

<<FILL: controls or conditions already in place or inherited that lower likelihood or impact, with tokens>>

## External and supply chain risk

<<FILL: the risk from each connection and information exchange outside the boundary, each external provider (services, whether they meet the requirements, assurances, trust and the response when it falls short) and each supplier (ra.yaml external), with tokens>>

## Risk summary

<<FILL: the risks in priority order, how risks of similar level were refined (immediate and future impact, cumulative impact, coupling) under a method tied to the mission and risk tolerance, how borderline values were settled, the uncertainty, the ones that drive requirements and tailoring, and to whom and how the results are communicated and shared (ra.yaml prioritization and communication), with tokens>>

## Privacy risk

<<FILL: risks to individuals from the processing of PII, or a sentence saying the system processes none; for a system with PII, the nature of the processing and its impact on individuals, and each legal and policy privacy requirement evaluated for applicability, OMB A-130 among them with the obligations the privacy control baseline does not meet and the separate steps for them, and the ART-REQ requirements that carry each applicable one (ra.yaml privacy; PRIV-007), with tokens>>

## Maintenance

<<FILL: the risk factors kept under ongoing monitoring, how often they are monitored and the circumstances in which this assessment is updated, following the organization's approach in ART-ORG-CONTEXT and conmon.yaml risk_assessment; whether the purpose, scope and assumptions still hold, with tokens>>

<!-- R-2 and M-3 do not rewrite the sections above: each appends "## Update (R-2)" or
     "## Update (M-3)" with the date, what changed (new findings, threats or POA&M status) and
     the revised risks, and adds itself to touched_by. -->
