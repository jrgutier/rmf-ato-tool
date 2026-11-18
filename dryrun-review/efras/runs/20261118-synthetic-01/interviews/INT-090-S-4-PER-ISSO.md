---
interview_id: INT-090
run_id: 20261118-synthetic-01
task: S-4
persona: PER-ISSO
date: 2026-11-18
topics: [events logged, review, protection and retention of audit records]
---
# INT-090 — S-4 — PER-ISSO

### Q1 {#INT-090.Q1}
Asked of: PER-ISSO · Task: S-4 · Control focus: au-2
Which events does each component log, why are they enough, and how often is the list reviewed?
**A1 {#INT-090.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]] [[product/test-results.md#dt-2]]
> The load balancer and WAF log every request and rule hit (CMP-EDGE); the API logs sign-in,
> role changes, data exports, admin actions and failed authorization (CMP-API); the cluster audit
> log records every API server call (CMP-K8S); the database audit extension records logins,
> privilege changes and DDL (CMP-DB); and the cloud account activity log records console and API
> actions. All of it lands in CMP-LOGS. Those events let us reconstruct who saw or exported which
> unit's data and who changed what, which is what an investigation of a PII or CUI incident needs.
> We picked them with the CSSP, whose use cases need the export and privileged events. I review the
> event list annually and with each major release.

### Q2 {#INT-090.Q2}
Asked of: PER-ISSO · Task: S-4 · Control focus: au-6, au-9
How are audit records reviewed and protected?
**A2 {#INT-090.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]] [[INT-072.A1]]
> Weekly I review the report of privileged actions, exports and denied requests from CMP-LOGS; the
> CSSP watches the forwarded stream around the clock on its use cases. Break-glass use and export
> volume spikes page the on-call engineer. I report findings to the ISSM, and anything that looks
> like misuse of PII also to the Component privacy office; the CSSP reports its findings to me and
> the ISSM. When the CSSP or the Component raises the threat level, I move to a daily review. The
> log store is write-once for 90 days, only the auditor role and I can read it, no one can delete
> it, and any change to its access policy alerts me and the ISSM.

### Q3 {#INT-090.Q3}
Asked of: PER-ISSO · Task: S-4 · Control focus: au-11
How long are audit records kept today?
**A3 {#INT-090.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[INT-083.A2]]
> Ninety days in our store. The CSSP keeps its copy for a year, but our own copy is short of the
> one-year Component rule until the archive tier ships in release 1.6.
