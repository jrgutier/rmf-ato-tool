---
interview_id: INT-115
run_id: 20261118-synthetic-01
task: S-4
persona: PER-CSSP
date: 2026-11-18
topics: [security monitoring of forwarded logs, monitoring objectives, reporting]
---
# INT-115 — S-4 — PER-CSSP

### Q1 {#INT-115.Q1}
Asked of: PER-CSSP · Task: S-4 · Control focus: si-4
What do you monitor for EFRAS, against which objectives and techniques, and what do you report to whom?
**A1 {#INT-115.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-072.A1]] [[INT-091.A1]] [[product/architecture.md#logging]] [[product/test-results.md#dt-2]] [[INT-075.A2]]
> We correlate the logs EFRAS forwards, 24x7: the load balancer and WAF, the application's
> sign-in, role change, export, admin and denied events, the cluster audit log, the database
> audit and the cloud account activity. Our objectives are attacks on the edge, account
> compromise, privilege misuse, data exfiltration and unauthorized connections; our techniques
> are signature and use-case correlation, behavioral baselines for exports and sign-ins, and
> threat intelligence matching. DT-2 showed export events reach us within 5 minutes. We raise
> the monitoring level on a CPCON change or an AO's direction. The Component's counsel reviewed
> our monitoring, and users get the monitoring notice in the sign-in banner. We protect the
> monitoring data, which carries maintainer identifiers, with encryption and access limits under
> our agreement. We send alerts to the ISSO and the on-call engineer as needed, and a monthly
> summary to the ISSO and the ISSM.
