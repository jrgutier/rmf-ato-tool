---
interview_id: INT-114
run_id: 20261118-synthetic-01
task: S-4
persona: PER-ISSO
date: 2026-11-18
topics: [patching and flaw remediation, retention and purge of PII and outputs]
---
# INT-114 — S-4 — PER-ISSO

### Q1 {#INT-114.Q1}
Asked of: PER-ISSO · Task: S-4 · Control focus: si-2
How are flaws found, tested and fixed in EFRAS's own parts, and how fast?
**A1 {#INT-114.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#updates]] [[product/architecture.md#configuration]] [[product/conops.md#limitations]] [[product/test-results.md#pipeline-1-5]]
> Flaws reach us from the pipeline scans, the weekly scan, CSSP alerts and the factory. Each
> becomes a ticket I track. Fixes ship as pipeline releases every three weeks, through the same
> gates and my sign-off, and are tested in pre-production first; an emergency patch can go out
> within 48 hours. Worker nodes roll monthly to the provider's latest hardened image. Our rule
> is security updates installed within 30 days of release, critical ones by emergency patch.
> We miss it today for the report-rendering container: the upstream fix for the two high
> vulnerabilities is out, but the factory's hardened base image that carries it is not, so
> release 1.5.2 waits until 2026-12-10. Every fix is a change under the CM process.

### Q2 {#INT-114.Q2}
Asked of: PER-ISSO · Task: S-4 · Control focus: si-12
How long is information kept in EFRAS and in what it outputs, and what removes it?
**A2 {#INT-114.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/privacy.md#minimization]] [[product/architecture.md#logging]] [[INT-075.A1]]
> Maintainer PII stays only while its maintenance action is inside the 5-year analysis window;
> the ingest worker purges older records monthly, and I check the purge log each month. Readiness
> data follows the same window under the Component records schedule. The report cache in object
> storage expires after 30 days by a lifecycle rule. Exports carry the CUI marking and the
> handling notice, and recipients keep them under their own records rules. Audit logs: 90 days
> here and one year at the CSSP, which is the gap in AU-11, not here.
