---
interview_id: INT-084
run_id: 20261118-synthetic-01
task: S-3
persona: PER-ISSM
date: 2026-11-18
topics: [arrangement of the leveraged authorizations, review of the providers' packages, requirements verified outside the control set]
---
# INT-084 — S-3 — PER-ISSM

### Q1 {#INT-084.Q1}
Asked of: PER-ISSM · Task: S-3
The access point, the software factory and the CSSP each carry only part of the controls they
offer. How does EFRAS inherit from each of them: as an approved common control provider, from
another organizational system, or as an external service?
**A1 {#INT-084.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[INT-071.A4]] [[INT-072.A1]]
> The access point and the software factory are DoD systems in their own right, each with its
> own ATO from its own AO; we inherit part of SC-7 from the access point and part of SA-11, SR-3
> and SR-11 from the factory, so each is another organizational system we inherit from, with a
> valid ATO, not a common control package written for us. The CSSP is different: we consume a
> monitoring and incident response service under the ECSSP-ARSPO service agreement, and the CSSP
> runs it under its own authorization. That is a service under agreement, so I would call it an
> external service, even though it is provided inside DoD. None of the three offers a control
> we can inherit whole; the allocations stay hybrid.

### Q2 {#INT-084.Q2}
Asked of: PER-ISSM · Task: S-3
When did you review each provider's authorization package, what did you weigh, and what is the
risk of the component that joins it to EFRAS?
**A2 {#INT-084.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[product/architecture.md#components]] [[ART-ORG-CONTEXT]]
> I reviewed all three packages in eMASS today, 2026-11-18, well before any authorization
> decision. The access point: ATO of 2025-01-10, under two years old, same NIPRNet-to-cloud
> environment we use, authorized at moderate, within the AO's tolerance; the risk sits in
> CMP-ECAP, the inspection path every inbound session crosses, and a misrule there would block
> or expose the edge. The software factory: ATO of 2025-10-01, current, a DevSecOps environment
> outside our boundary, moderate; CMP-SWF delivers every image we run, so a compromised pipeline
> is the main supply chain risk, which SR-3 and SR-11 cover in part. The CSSP: its service
> agreement dates from 2026-04-01 under its own ATO, the environment is the Component's SOC,
> moderate; CMP-ECSSP only receives forwarded logs, so the integration risk is that a broken
> forwarder leaves us unmonitored. For both privacy overlays I checked that each provider
> handles the PII it touches under its own privacy controls: the access point and the CSSP see
> maintainer IDs in traffic and logs, the factory sees none.

### Q3 {#INT-084.Q3}
Asked of: PER-ISSM · Task: S-3
When do the access point's and the software factory's ATOs end?
**A3 {#INT-084.A3}** respondent: simulated · tag: SIMULATED · basis: [[ASM-017]]
> Neither package gives an end date in what the program holds. Our Component grants three-year
> ATOs, so I am working to 2028-01-10 for the access point and 2028-10-01 for the factory, and
> I will confirm both in eMASS. Record that as an assumption.

### Q4 {#INT-084.Q4}
Asked of: PER-ISSM · Task: S-3
REQ-11 (DoD IT Standards Registry) and REQ-12 (Section 508) have no control in the set. How is
conformance to them verified, and which selected control carries that verification?
**A4 {#INT-084.A4}** respondent: simulated · tag: SIMULATED · basis: [[ART-REQ]] [[INT-079.A3]] [[INT-071.A3]]
> Neither has a control that implements it; both are verified, not implemented. The developer
> verifies them in its test and evaluation: standards conformance by analysis of the interfaces
> against the registry, accessibility by testing the web pages. That is SA-11, developer testing
> and evaluation, so trace both to sa-11 and say plainly that the trace stands for "verified
> through developer test and evaluation, outside the control set". I have no test result for
> either in the product material today, so the assessor will find no evidence yet.
