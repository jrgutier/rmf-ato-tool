---
artifact_id: ART-ORG-CONTEXT
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: P-1
touched_by: [P-1]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Organizational risk context

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-ORG-CONTEXT (playbook: playbooks/P/P-org-context.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. The checkable
     record is artifacts/data/org-context.yaml (template templates/data/org-context.yaml);
     this Markdown states the same context in prose. Delete this comment. -->

## RMF role assignments

<<FILL: table: role | persona ID | assigned to | appointed by, for AO, AODR, Component CIO and CISO, SCA, PM or SO, ISSM, ISSO, privacy officer and each common control provider, with tokens>>

<!-- P-2..P-7 each append their section below, in this order, and add themselves to
     touched_by. An optional task that is not performed (P-4, P-6) still appends its heading
     with one traced sentence saying the organization has none.
     - P-2 "## Risk management strategy and risk tolerance": how risk is framed, assessed,
       responded to and monitored; the SP 800-30 rating scale; the tolerance statement;
       which risk levels need Component CIO concurrence before an ATO; the maximum
       authorization period; the organizational remediation period for weaknesses; and how
       risk assessments are maintained: what triggers an update, how often, what is
       updated and how results are communicated (S-5 records it in conmon.yaml
       risk_assessment, M-4 applies it).
     - P-2 "## Privacy program": the Component privacy and civil liberties program, its SCOP
       and PCLO with their staffing and reporting lines to the DoD SAOP, complaint and
       alleged violation procedures, training and awareness, how privacy controls are
       designated (program management, common, system-specific, hybrid), and whether the
       SCOP approves or, in an OSD Component, primarily advises.
       P-2 also appends "## Software program": the Component's direction under DoWI 8430.01
       for software the organization develops or deploys: governance adapted to iterative
       development and continuous delivery, delegated decisions verified by automated
       evidence, the software workforce (DoW Cyber Workforce Framework work roles, training,
       career paths, performance assessments), records of software assets, and any exception
       to the issuance requested through the E2P Portal. Each system's software.yaml program
       section (S-4) applies it.
     - P-3 "## Organization-level risk assessment": enterprise threats, dependencies and
       aggregated risks, and when the assessment was last updated.
     - P-4 "## Organizationally tailored baselines and profiles": approved or directed
       tailored baselines, overlays and CSF profiles systems must start from; an overlay the
       organization develops itself also goes in org-context.yaml developed_overlays.
     - P-5 "## Common controls available for inheritance": table: provider | persona ID |
       controls offered | full or partial | provider authorization and its status.
     - P-6 "## Impact-level prioritization": how systems of the same impact level are
       placed in low, moderate and high sub-categories.
     - P-7 "## Organizational continuous monitoring strategy": the metrics, frequencies and
       reporting every system's strategy (S-5) must implement; and the Component's
       vulnerability management program (DoDI 8531.01 2.10) that S-5 and M-3 read: the
       organizations designated to direct and manage it and to coordinate with JFHQ-DODIN, the
       asset, configuration, remediation and mitigation programs that support it, the
       prioritization and scheduling plan for deploying patches, updates and directed
       actions, the guidance to system owners on mitigation deployment and who may accept
       risk, what the Component requires system owners to mitigate, and its audits of
       patching, compliance and reporting. -->
