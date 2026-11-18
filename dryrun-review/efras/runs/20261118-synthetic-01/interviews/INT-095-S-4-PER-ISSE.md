---
interview_id: INT-095
run_id: 20261118-synthetic-01
task: S-4
persona: PER-ISSE
date: 2026-11-18
topics: [contingency plan, testing, backups]
---
# INT-095 — S-4 — PER-ISSE

### Q1 {#INT-095.Q1}
Asked of: PER-ISSE · Task: S-4 · Control focus: cp-2
What state is the contingency plan in?
**A1 {#INT-095.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/conops.md#availability]] [[ART-BIA]]
> Drafted, not approved and not exercised. The draft covers the essential function (daily
> readiness reporting, which tolerates 72 hours), the recovery objectives of 24 hours for time
> and for data, restoration order database first, then ingest, API and web, the ERST on-call
> engineers, the ISSO and the PM as contingency roles, fallback to EMIS reports during an outage,
> and restoring with the same templates so the controls come back as built. It is coordinated with
> incident handling through the CSSP ticket path, kept in the program repository with access
> limited to the program, and goes to the PM for approval with this plan set. Once approved we
> give it to the on-call engineers, the ISSO, the ISSM and the EMIS and CSSP points of contact,
> review it annually and update it after any test or real event.

### Q2 {#INT-095.Q2}
Asked of: PER-ISSE · Task: S-4 · Control focus: cp-4, cp-9
What has been tested, and how are backups taken?
**A2 {#INT-095.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#dt-2]] [[product/conops.md#limitations]] [[product/architecture.md#components]] [[product/architecture.md#configuration]]
> Database point-in-time restore to a new instance was tested once in DT-2 and took 3 h 10 min.
> A full regional failover of the cluster has never been tested; the tabletop and failover test
> are planned for 2027-02, and we will test annually after that. Backups: the managed database
> keeps continuous point-in-time recovery with daily snapshots, encrypted with our keys (CMP-DB);
> the object storage buckets are versioned (CMP-OBJ); system-level information and documentation
> are the templates, images and documents in version control, so every merge is a backup. The
> provider runs the snapshot and storage durability machinery.
