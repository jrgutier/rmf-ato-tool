---
interview_id: INT-124
run_id: 20261118-synthetic-01
task: S-4
persona: PER-ISSE
date: 2026-11-18
topics: [contingency plan, recovery times, preventive measures, recovery strategy, exercises]
---
# INT-124 — S-4 — PER-ISSE

### Q1 {#INT-124.Q1}
Asked of: PER-ISSE · Task: S-4 · Control focus: cp-2 (contingency plan, BIA)
For each business process, what are the maximum tolerable downtime, recovery time, recovery point and reprocessing time, and what does recovery need?
**A1 {#INT-124.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-095.A1]] [[product/conops.md#availability]] [[ART-BIA]] [[product/test-results.md#dt-2]]
> Readiness reporting (BP-01): 72 hours tolerable, 24-hour recovery time and 24-hour recovery
> point (one nightly ingest), and about 4 hours to re-run the missed ingest and rebuild the
> dashboards. Forecasting (BP-02) and fleet analysis (BP-03): 168 hours tolerable; they come
> back after BP-01, within 48 hours, with the same 24-hour recovery point, and the forecast
> re-scores in about 2 hours. Recovery needs the database and its snapshots, the object
> storage, the key service (no keys, no data), the cluster, the pipeline and templates in the
> software factory, the identity broker, the access point and the EMIS and supply extracts,
> plus two on-call engineers. None of these processes supports a mission essential function.

### Q2 {#INT-124.Q2}
Asked of: PER-ISSE · Task: S-4 · Control focus: cp-2, cp-4, cp-9
What strategy recovers the system, what alternatives were weighed, and what has been proved?
**A2 {#INT-124.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-095.A2]] [[INT-096.A1]] [[product/conops.md#limitations]] [[product/architecture.md#components]]
> The database runs a primary with a provider-managed standby in a second availability zone,
> and node groups span three zones, so a zone failure fails over on its own. For a regional
> loss the strategy is a rebuild in the provider's second IL4 region from the templates and
> signed images, with the database restored from cross-region snapshot copies: a cold
> alternate region. We weighed a warm standby region (about four times the run cost, recovery
> in 2 hours) and a hot active-active design (higher still, and not needed for a 72-hour
> tolerance) against the cold rebuild (only snapshot storage, about 18 hours estimated). We
> chose the cold rebuild. What is proved: the database point-in-time restore, once, in
> pre-production during DT-2, 3 h 10 min. The regional rebuild and failover have never been
> tested; the 18-hour estimate is not proved. Tabletop and failover test are planned for
> 2027-02. Backups: point-in-time recovery plus daily snapshots of CMP-DB kept 35 days, copied
> to the second region and encrypted with program keys replicated there; versioned object
> storage; templates and image manifests in version control.

### Q3 {#INT-124.Q3}
Asked of: PER-ISSE · Task: S-4 · Control focus: cp-2, cp-4
Who activates and runs recovery, and which exercises will test the plan?
**A3 {#INT-124.A3}** respondent: simulated · tag: SIMULATED · basis: [[INT-095.A1]] [[INT-095.A2]] [[INT-098.A1]]
> The PM activates the plan; the ISSM is the successor when the PM cannot be reached. I
> coordinate recovery as the ISSCP coordinator; the ERST technical lead leads the recovery
> team (on-call engineers), with the senior on-call engineer as alternate; the ISSO leads
> notification and the security checks. Exercises: a tabletop in 2027-02 on a ransomware-style
> compromise of the cloud account in which we lose the account and its connectivity and fall
> back to EMIS reports, testing the work-arounds and fall-backs; a functional regional
> failover test in 2027-02 that rebuilds in the second region from the templates and restores
> the database from the copied snapshots; and the database restore test annually. After that,
> each yearly. Both critical suppliers (ERST and the cloud provider) take part; the CSSP joins
> the tabletop.
