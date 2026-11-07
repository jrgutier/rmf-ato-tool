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
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Method and scope

<<FILL: the SP 800-30 approach used, the assessment scope and assumptions, and the likelihood, impact and risk scales including Table I-2, with tokens>>

## Threat sources and events

<<FILL: table: TE-# | threat event | threat source | likelihood | impact | initial risk, with tokens>>

## Vulnerabilities and predisposing conditions

<<FILL: weaknesses and conditions that make the threat events more likely or more harmful, with tokens>>

## Mitigating conditions

<<FILL: controls or conditions already in place or inherited that lower likelihood or impact, with tokens>>

## Risk summary

<<FILL: the risks in priority order and the ones that drive requirements and tailoring, with tokens>>

## Privacy risk

<<FILL: risks to individuals from the processing of PII, or a sentence saying the system processes none, with tokens>>

## Maintenance

<<FILL: the risk factors kept under ongoing monitoring, how often they are monitored and the circumstances in which this assessment is updated, following the organization's approach in ART-ORG-CONTEXT and conmon.yaml risk_assessment; whether the purpose, scope and assumptions still hold, with tokens>>

<!-- R-2 and M-3 do not rewrite the sections above: each appends "## Update (R-2)" or
     "## Update (M-3)" with the date, what changed (new findings, threats or POA&M status) and
     the revised risks, and adds itself to touched_by. -->
