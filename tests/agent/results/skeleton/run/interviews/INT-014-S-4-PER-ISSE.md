---
interview_id: INT-014
run_id: agent-skeleton
task: S-4
persona: PER-ISSE
date: 2026-10-29
topics: [configuration settings, event selection rationale]
---
# INT-014 — S-4 — PER-ISSE

### Q1 {#INT-014.Q1}
Asked of: PER-ISSE · Task: S-4 · Control focus: cm-6
**A1 {#INT-014.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#configuration]] [[ART-ORG-CONTEXT]]
> Every unit runs one signed OS image the developer builds from the General Purpose Operating
> System SRG plus the applicable application and web server guidance. The pipeline applies the
> hardening settings, so the gateway OS, collector, console and buffer database all ship in the
> most restrictive mode the mission allows, and it records every deviation from the guidance.

### Q2 {#INT-014.Q2}
Asked of: PER-ISSE · Task: S-4 · Control focus: cm-6
**A2 {#INT-014.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#configuration]] [[product/test-results.md#config-scan]]
> Deviations go to the RSSPO configuration control board, which approves them along with any
> change to the baseline. A configuration check runs nightly on each unit and reports drift to the
> SIEM. The 2026-09-30 witnessed SRG/STIG scan found the approved baseline on all 12 units and no
> drift in August or September.

### Q3 {#INT-014.Q3}
Asked of: PER-ISSE · Task: S-4 · Control focus: au-2
**A3 {#INT-014.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]] [[product/conops.md#information]]
> Why those events: an investigation on ESG needs to know who signed in, who changed accounts,
> configuration or firewall rules, what software went on the box, whether a service was stopped,
> and whether someone paired a rogue sensor. The list covers each of those. Its one weakness is
> not in the list but in the `fieldtech` account: those events name the shared account, not a
> person.
