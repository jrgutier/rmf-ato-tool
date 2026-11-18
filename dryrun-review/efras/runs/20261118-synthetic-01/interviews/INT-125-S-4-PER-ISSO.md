---
interview_id: INT-125
run_id: 20261118-synthetic-01
task: S-4
persona: PER-ISSO
date: 2026-11-18
topics: [incident triage, incident lead, evidence, reporting paths, recovery after an incident]
---
# INT-125 — S-4 — PER-ISSO

### Q1 {#INT-125.Q1}
Asked of: PER-ISSO · Task: S-4 · Control focus: ir-4, ir-8 (incident response plan)
How is an incident triaged and escalated, which fields are tracked, who leads, and how is evidence kept?
**A1 {#INT-125.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-098.A1]] [[INT-099.A1]] [[INT-099.A3]] [[product/architecture.md#logging]]
> I am the incident lead for EFRAS and keep the ticket and every record of the response. The
> CSSP declares and categorizes from the forwarded logs and opens a ticket to me and the ISSM;
> users, engineers and the cloud provider or the access point can also report to the CSSP
> operations center or to me. Priority comes from the data at risk (maintainer PII or readiness
> data first), whether a privileged identity is involved, whether the attack is active and
> how far it reaches across components. Categories follow the CSSP's playbook: unauthorized
> access, malicious code, denial of service, improper usage, PII breach, spillage. Each
> ticket tracks the time of detection and report, category, affected components and data,
> actions taken, who decided, status and closure. The CSSP and the on-call engineer preserve
> logs, snapshots of the affected workloads and database, and cloud activity records; I log
> the chain of custody. Containment holds until the CSSP confirms no further activity for 72
> hours and eradication (rebuild from signed images, credential rotation) is verified.
> Escalation: anything touching PII or a privileged identity goes to the ISSM and the AODR at
> once; an incident not contained within 24 hours goes to the PM and the AO.

### Q2 {#INT-125.Q2}
Asked of: PER-ISSO · Task: S-4 · Control focus: ir-6
Who is told of each kind of incident, under which issuance, and how fast?
**A2 {#INT-125.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-098.A2]] [[INT-099.A2]] [[INT-106.A1]] [[product/conops.md#information]]
> Everyone reports to the CSSP and to me within one hour. The CSSP reports to JFHQ-DODIN
> through the DoD CERT channel under CNSSI 1010 and the DoD incident handling timelines, and
> I tell the AO through the AODR and our chain of command. A suspected PII breach goes to the
> Component privacy office within one hour, under DoD 5400.11-R. An unauthorized disclosure of
> CUI goes to the Component CUI program office under DoDM 5200.01 Volume 4. EFRAS holds no
> classified information, but a classified spillage onto it is reported at once to the
> Component security manager under DoDM 5200.01 Volume 3, which identifies it as a negligent
> discharge and investigates whether it was willful, negligent or inadvertent. Something that
> looks like a federal crime goes to the defense criminal investigative organization, law
> enforcement and the IG DoD; anomalous user activity goes to the Component investigative
> authority with the audit data under chain of custody. A cybersecurity deficiency behind a
> breach goes to the IG DoD. ERST is a cleared contractor: a loss on its corporate systems
> involving EFRAS information is reported under DoD 5220.22-M to DCSA.

### Q3 {#INT-125.Q3}
Asked of: PER-ISSO · Task: S-4 · Control focus: ir-4, cp-2
When does recovery start and end, and how do you know restored components are clean?
**A3 {#INT-125.A3}** respondent: simulated · tag: SIMULATED · basis: [[INT-095.A1]] [[INT-099.A1]] [[product/test-results.md#dt-2]]
> Recovery starts when the CSSP and I agree that containment holds and the PM authorizes it;
> the AODR is told. We restore from signed images and the templates and the database from the
> last snapshot taken before the compromise, checking image signatures and snapshot hashes
> before use and scanning and comparing the restored account against the baseline before
> users return, in the order of the contingency plan: database, ingest, API, web. The CSSP
> watches the restored system closely for 30 days. Recovery ends when the restored system
> passes the checks and the PM declares normal operations; I write the after-action report
> within 10 working days, and its lessons go to the plan, the runbooks and training.
