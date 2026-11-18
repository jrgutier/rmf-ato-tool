---
interview_id: INT-166
run_id: 20261118-synthetic-01
task: A-3
persona: PER-CSSP
date: 2026-11-20
topics: [CSSP handling playbook, onward incident reporting, monitoring use cases, external vulnerability scan]
---
# INT-166 — A-3 — PER-CSSP

### Q1 {#INT-166.Q1}
Asked of: PER-CSSP · Task: A-3 · Control focus: ir-4
What evidence shows your handling of an EFRAS incident would follow the same playbook, rigor and reporting as for the other systems you serve?
**A1 {#INT-166.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-SVCA]] [[ART-IRP]] [[INT-098.A1]]
> The service agreement binds EFRAS to our one handling playbook: we detect and analyze from the
> forwarded logs 24x7, declare and categorize, and open a ticket with the program. The playbook,
> our DoD O-8530.01-M evaluation and the monthly service report are the evidence; I can give you
> the October report. We cannot act inside the EFRAS cloud account, so containment and recovery
> rest on the program's on-call engineers.

### Q2 {#INT-166.Q2}
Asked of: PER-CSSP · Task: A-3 · Control focus: ir-6
Who do you report EFRAS incident information to, and where is that written?
**A2 {#INT-166.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-098.A2]] [[ART-IRP]]
> To JFHQ-DODIN and the DoD central point of contact within the DoD timelines, and to the AO's
> office through the AODR. That is in the service agreement and in our reporting procedure,
> which applies to every system we serve.

### Q3 {#INT-166.Q3}
Asked of: PER-CSSP · Task: A-3 · Control focus: si-4
Which EFRAS feeds do you receive and which use cases do you run against them?
**A3 {#INT-166.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]] [[product/test-results.md#dt-2]]
> We receive the edge and WAF logs, the application's sign-in, role change, export, admin and
> denied events, the cluster audit log, the database audit and the cloud account activity log.
> The use cases cover attacks on the edge, account compromise, privilege misuse and export
> volume, with sign-in and export baselines and threat intelligence matching. A missing-feed
> alert fires if the forwarder stops. Alerts go to the ISSO and the on-call engineer, and a
> monthly summary goes to the ISSO and the ISSM.

### Q4 {#INT-166.Q4}
Asked of: PER-CSSP · Task: A-3 · Control focus: ra-5
What does your monthly external scan of the EFRAS edge show?
**A4 {#INT-166.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#pipeline-1-5]]
> We scan only the edge; the October scan found the verbose server header the pipeline's dynamic
> scan had already found, and it was gone after release 1.5.1. We see nothing inside the
> account, so the report container's findings come to us from the program's pipeline, not
> from our scan.
