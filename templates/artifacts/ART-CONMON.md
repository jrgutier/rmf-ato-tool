---
artifact_id: ART-CONMON
run_id: "<<FILL: run_id from run.yaml>>"
produced_by_task: S-5
touched_by: [S-5]
sources: ["<<FILL: trace tokens the whole artifact rests on>>"]
---
# Continuous monitoring strategy

<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->

<!-- Template for ART-CONMON (playbook: playbooks/S/S-5.md). Replace every <<FILL: ...>> placeholder with traced
     prose; each ## section needs at least one [[TOKEN]] (playbooks/_shared/tagging-and-traceability.md).
     Never write between the rmf:facts markers and never restate system facts. Delete this comment. -->

## Strategy overview

<<FILL: how the system strategy implements the organizational continuous monitoring strategy in ART-ORG-CONTEXT and supports ongoing authorization; how compliance, effectiveness and change are each monitored (conmon.yaml monitoring), with tokens>>

## Monitoring frequencies

<<FILL: per control family, how often and by what method effectiveness is monitored and who does it, and each control monitored at another minimum frequency (overrides); the records live in artifacts/data/conmon.yaml; with tokens>>

## Frequency criteria

<<FILL: the criteria (frequency_criteria FC-nn: volatility, impact level, critical functions, known weaknesses, threat and vulnerability information, risk assessment results, reporting requirements, risk tolerance, resources) behind each frequency the organizational strategy does not set, who established them and with which officials, and the approval of the strategy and minimum frequencies by the AO or AODR (conmon.yaml approval), with tokens>>

## Privacy continuous monitoring

<<FILL: for a system processing PII, the privacy continuous monitoring strategy: the SAOP's guidance on the ongoing monitoring of privacy controls, each privacy control of the baseline with its organization-defined assessment frequency, and each control added to the strategy with the SAOP's consultation (conmon.yaml privacy; PRIV-006); or a sentence saying the system processes no PII, with tokens>>

## Automated tools and data

<<FILL: each automated tool (TOOL-nn): the controls it assesses by the test method, how often, the analysis and reporting of its results, why it was chosen and how it is validated and kept up; for a desired state strategy the actual state, the comparable desired state and how defects are computed; how monitoring data is collected, stored, analyzed, retrieved and delivered within and between tiers, where monitoring is automated and where it is not, and why (conmon.yaml tools and architecture), with tokens>>

## Ongoing authorization triggers

<<FILL: the time-driven trigger in days and each event that triggers a review of the authorization, as in conmon.yaml ongoing_authorization; each event criterion (events EV-nn) with its threshold and whether it triggers an assessment, a reauthorization or both; how often the authorization boundary is revisited (boundary_review), with tokens>>

## Threat monitoring

<<FILL: who watches threat actor activity, new protective techniques and the threat environment where the system is deployed, from which sources and how often, and how a major change feeds M-1 and M-3 (conmon.yaml threat_monitoring), with tokens>>

## Metrics and reporting

<<FILL: each metric (MET-nn), what it measures, how often, who receives it and which Monitor tasks use it; who receives posture reports, how often and in what form, as in conmon.yaml reporting, with tokens>>

## Risk assessment upkeep

<<FILL: how the system risk assessment is kept current under the organization's approach in ART-ORG-CONTEXT: frequency, triggers, what is updated and to whom results are communicated (conmon.yaml risk_assessment); M-4 applies it, with tokens>>

## Security measurement

<<FILL: the security-relevant information needs, the measures that satisfy them with their acceptable parameters and users, and the procedures for collection, analysis, access and reporting, as in conmon.yaml measurement, with tokens>>

## Vulnerability management

<<FILL: how the system runs the five steps of the DoD vulnerability management process (DoDI 8531.01 Section 3) and which records support it; how vulnerabilities are identified (scans with NIST SP 800-115 as reference, CVE, automation before manual work and why each manual activity is manual, incident reports and logs cross-referenced with CVE, risk assessment data and vendor bulletins); the analysis tools from development through operational test, operations and sustainment to retirement, and where JFAC assistance or licenses are used; the monthly authenticated and non-authenticated scans; where patches come from for what enterprise patching does not reach, the scan of its reach and how non-compliant devices are brought into compliance; the metrics computed and maintained over time to evaluate patching effectiveness (mean time to patch, patch deployment success rate, vulnerability exposure or others), each a metric of the strategy; the central log repository or SIEM; a provider's plan and the AO's approval of it, as in conmon.yaml vulnerability_management, with tokens>>

## Roles and tools

<<FILL: who collects, analyzes and reports monitoring data, including the CSSP and common control providers, and each operations and sustainment activity delegated to an external partner with its agreement (conmon.yaml delegations); the tools used; which asset classes detection covers at all times (networks, the physical environment, personnel activity, external providers, computing) and how monitoring is tuned against false positives and negatives, as in conmon.yaml detection_coverage and tuning, with tokens>>

<!-- M-2 updates artifacts/data/conmon.yaml when ongoing assessments change a frequency or
     method, appends "## Changes after ongoing assessment" (what changed and why), and adds
     M-2 to touched_by. -->
