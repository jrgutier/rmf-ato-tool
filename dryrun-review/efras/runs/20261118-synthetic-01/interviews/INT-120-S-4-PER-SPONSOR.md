---
interview_id: INT-120
run_id: 20261118-synthetic-01
task: S-4
persona: PER-SPONSOR
date: 2026-11-18
topics: [mission owner review of the cloud package, activity tracking checklist, external assessments, user activity monitoring]
---
# INT-120 — S-4 — PER-SPONSOR

### Q1 {#INT-120.Q1}
Asked of: PER-SPONSOR · Task: S-4 · Control focus: cloud (DoD CIO reciprocity guide)
As mission owner, did you review the cloud offering's provisional authorization, and what did you look at?
**A1 {#INT-120.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-119.A1]] [[INT-117.A1]] [[product/conops.md#information]]
> Yes, on 2026-11-18, with the product manager and the AO's office, from the eMASS package: the
> kinds of data it may host (CUI, including our maintainer PII), the IL4 level, its conditions,
> the risks it leaves to tenants in the customer responsibility matrix, the cybersecurity
> services it offers, and its annual assessment. IL4 fits our readiness data and PII. We
> negotiated nothing beyond the enterprise contract.

### Q2 {#INT-120.Q2}
Asked of: PER-SPONSOR · Task: S-4 · Control focus: cloud (DTM 24-001)
Who performs each cybersecurity activity for EFRAS in the cloud, and how are external assessments requested?
**A2 {#INT-120.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-118.A2]] [[INT-119.A2]] [[INT-113.A1]] [[INT-107.A2]] [[product/architecture.md#leveraged]] [[product/test-results.md#pentest]]
> The product manager and I drew up the activity tracking checklist with the CSSP and the AO's
> office on 2026-11-18. The CSSP does the external scans, threat correlation, malware
> notification, network security monitoring, enclave monitoring, CPCON notification, incident
> categorization, reporting, analysis and the law enforcement and counterintelligence hand-offs.
> The access point does boundary cyberspace protection. The program, through ERST and the
> factory, does the web scans, endpoint security and visibility on the worker nodes, the
> configurations, mitigating and tracking vulnerabilities, malware protection, application
> protection at the WAF, CPCON implementation and incident handling inside the account. The
> Component red team, a certified DCRT, does red team and penetration testing; the Component
> cyber assessment team does DCAT work on request; the Component insider threat program
> correlates user activity data. To request an external assessment, the product manager sends
> the need to me and the AO's office; I approve it in writing, the team gets our architecture
> diagrams and description, and we coordinate it with any CCRI or CORI so the two do not
> collide. Results go to us, the AO and the CSSP. The red team's penetration test of
> pre-production ran 2026-10-27 to 2026-10-31; I approved it in writing on 2026-10-20, the team
> sent its mission details to JFHQ-DODIN on 2026-10-22, constrained by safety, real-world
> mission execution and operational security, and its report with remediation recommendations
> and lessons learned went to the program and the CSSP.

### Q3 {#INT-120.Q3}
Asked of: PER-SPONSOR · Task: S-4 · Control focus: cloud (DTM 24-001 UAM)
How is user activity monitored on EFRAS?
**A3 {#INT-120.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]] [[INT-115.A1]]
> Not outsourced: the program's own logs detect anomalous user activity and keep the audit data,
> the CSSP correlates them, and the Component insider threat program correlates with law
> enforcement and counterintelligence; its analysts are trained for that. Our procedures cover
> the monitoring itself, the response to anomalous activity, the chain of custody and the
> preservation of audit data. The data goes to the program and the CSSP.
