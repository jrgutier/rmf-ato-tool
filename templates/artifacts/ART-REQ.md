---
artifact_id: ART-REQ
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: P-15
touched_by: [P-15]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Security and privacy requirements and allocation

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-REQ (playbook: playbooks/P/P-15.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Sources of requirements

<<FILL: the laws, policies, capability requirements, stakeholder needs and risk assessment results the requirements come from, and the DoD design policy statements of artifacts/data/requirements.yaml design_policy (each one that applies, and why a conditional one does not), with tokens>>

## Protection needs

<<FILL: the stakeholders' security concerns, loss concerns per asset and trust expectations from ART-STAKE, each protection need by NEED ID with its success criteria, priority and rationale, and when they were last reassessed, with tokens>>

## Security and privacy requirements

<<FILL: table: REQ-## ID | requirement | traces to (NEED, DP or parent REQ) | priority | measure and criticality | verification method, one testable requirement per row as in requirements.yaml, with tokens>>

## Privacy Act rules

<<FILL: for a system of records, each Privacy Act rule no control states (direct collection from the individual, the bars on disclosure without consent and on First Amendment records, appeals of denied access or amendment requests, rules of conduct and penalties, contract provisions) and the requirement that carries it (requirements.yaml privacy_act; PRIV-007); or a sentence saying the system keeps no system of records, with tokens>>

## Derivation and security engineering

<<FILL: how the lead systems engineer derived the security and exportability requirements (the capability requirements document, CONOPS, operational mode summary and mission profiles that informed it, the methods used and what they cover), the key performance parameters and attributes and the measures they establish, where the requirements enter the system performance specification and the product support needs, the system security engineering practices by area and life cycle activity with the design principles they apply, and the level of assurance and why it is commensurate with the technology, program, system and mission objectives, summarizing requirements.yaml derivation and engineering by ID, with tokens>>

## Operational constraints

<<FILL: the security-relevant constraints on the solution by CON ID: those the security analysis drives, those from the stakeholders and the mission, and those implementation, integration, verification and transition raise, with tokens>>

## Analysis and agreement

<<FILL: how the requirement set was analyzed against the protection needs, the feedback the stakeholders got, the issues raised and how each was resolved, and each stakeholder's explicit agreement with the key decisions and their rationale, with tokens>>

<!-- P-17 adds an "Allocated to" column (component IDs from artifacts/data/boundary.yaml, the
     environment of operation, a common control provider or the contract) to the requirements
     table, appends "## Allocation" (how each requirement is split between the system, its
     elements and providers, and why, keeping the trace from need to verification both ways)
     and "## Contract requirements" (the cybersecurity requirements the RFP carries, the
     cyberspace work roles contractors perform, their qualification requirements, DFARS Subpart
     239.71 and how their qualifications are documented), and adds P-17 to touched_by. -->
