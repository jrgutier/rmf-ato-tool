---
interview_id: INT-136
run_id: 20261118-synthetic-01
task: I-1
persona: PER-ISSE
date: 2026-11-18
topics: [engineering methods, deviations from the plan, application checklist, third-party assurance]
---
# INT-136 — I-1 — PER-ISSE

### Q1 {#INT-136.Q1}
Asked of: PER-ISSE · Task: I-1 · Control focus: cm-6, sa-11
Were the controls built as the approved plan describes, and where does the build deviate from it?
**A1 {#INT-136.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#stig-scan]] [[product/test-results.md#pentest]] [[product/conops.md#limitations]] [[ART-SSP]]
> The build matches the approved plan's statements; the deviations are the ones the plan
> already names as partial: the two program-fixable PostgreSQL items, the CMP-REPORT library
> highs, the unsalted DoD ID hash in the exports, the untested regional failover and the
> break-glass accounts. Two corrections for the plan: the control plane and managed database
> items the scan marks inherited are the provider's settings under its IL4 provisional
> authorization, not deviations the ISSM approves; the configuration rules of this run give
> exception approval to the AO alone, so we record them as not applicable to our configuration
> and name the provider. And the PT-1 export scoping fix of 1.5.1 is in place and retested.

### Q2 {#INT-136.Q2}
Asked of: PER-ISSE · Task: I-1 · Control focus: cm-6
Which benchmark covers the application containers and the base image?
**A2 {#INT-136.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#configuration]] [[INT-135.A3]]
> The base image is hardened by the software factory to its own hardening standard; that is a
> supplier hardening guide we inherit, not a DISA checklist we ran. For our five containers the
> applicable checklist is the Application Security and Development STIG. Its checklist review has
> not been done for 1.5.0; I want the assessor to run it at A-3 with the developer's answers and
> the pipeline gate record as evidence, rather than us mark it ourselves. Until then it is
> not reviewed.

### Q3 {#INT-136.Q3}
Asked of: PER-ISSE · Task: I-1 · Control focus: sr-3, sa-9
What assurance do you hold for the third-party components?
**A3 {#INT-136.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[INT-119.A1]] [[INT-128.A1]]
> The managed services come with the cloud provider's IL4 provisional authorization and its
> customer responsibility matrix; the provider builds to the cloud computing SRG and applies
> the STIGs to its managed services. The base image and the pipeline come with the software
> factory's ATO, signed images and SBOMs. The open-source libraries are pinned by hash and
> scanned daily against the SBOMs.
