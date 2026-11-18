---
interview_id: INT-092
run_id: 20261118-synthetic-01
task: S-4
persona: PER-ISSM
date: 2026-11-18
topics: [assessment, information exchange, POA&M, continuous monitoring]
---
# INT-092 — S-4 — PER-ISSM

### Q1 {#INT-092.Q1}
Asked of: PER-ISSM · Task: S-4 · Control focus: ca-2
What is in place for control assessment today?
**A1 {#INT-092.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#top]] [[product/test-results.md#stig-scan]] [[ART-ORG-CONTEXT]]
> Only developer and developmental testing so far: the pipeline gates, DT-2, the SCA-witnessed
> STIG scan and the red team's penetration test, all offered for reuse. The assessor is not yet
> selected and there is no approved assessment plan; that is A-1 and A-2, before the
> authorization decision we need ahead of the 2027-02-01 MVCR deployment. After authorization the
> Component's strategy assesses a third of the controls each year, all of them within the
> authorization period, and results go to the AO, the PM and me.

### Q2 {#INT-092.Q2}
Asked of: PER-ISSM · Task: S-4 · Control focus: ca-3
Which information exchanges are approved, under which agreements, and how often are they
reviewed?
**A2 {#INT-092.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#interconnections]] [[product/conops.md#limitations]]
> Three: EMIS (CMP-INGEST pulls a nightly extract over mutual TLS), the supply status service
> (CMP-INGEST pulls through its API) and the identity broker (CMP-API). The supply SLA was signed
> on 2026-06-30 and the broker's enterprise onboarding approval dates from 2026-05-12. The EMIS
> memorandum of agreement is drafted and under legal review; the connection runs on an interim
> e-mail approval from the EMIS ISSM, with signature targeted for 2026-12-31. Each agreement is
> reviewed annually and on any change to the interface.

### Q3 {#INT-092.Q3}
Asked of: PER-ISSM · Task: S-4 · Control focus: ca-5, ca-7
How will the POA&M and continuous monitoring work for EFRAS?
**A3 {#INT-092.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[product/conops.md#limitations]] [[product/monitoring/README.md]]
> We track the seven known limitations with their fix releases in the program backlog today, but
> no POA&M exists yet; it is created in eMASS at A-6 from the assessment findings and updated
> monthly after that. The system-level monitoring strategy is S-5's, written under the Component
> strategy: weekly vulnerability scanning and log review, monthly configuration checks, quarterly
> account reviews, annual assessment of a third of the controls, and a monthly status report to
> the AO and quarterly to the risk board. Until S-5 approves it, none of that runs as a strategy.
