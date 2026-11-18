---
interview_id: INT-100
run_id: 20261118-synthetic-01
task: S-4
persona: PER-ISSE
date: 2026-11-18
topics: [nonlocal maintenance of the cluster and cloud account]
---
# INT-100 — S-4 — PER-ISSE

### Q1 {#INT-100.Q1}
Asked of: PER-ISSE · Task: S-4 · Control focus: ma-4
How is EFRAS maintained remotely, and how are those sessions approved, authenticated, recorded and closed?
**A1 {#INT-100.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/architecture.md#identity]] [[product/architecture.md#configuration]] [[product/architecture.md#logging]] [[product/architecture.md#updates]]
> All maintenance is nonlocal: there is no hardware of ours to touch. The six ERST engineers
> maintain the cluster, database and cloud account through the provider's privileged access path
> from ERST privileged access workstations, after CAC sign-in at the identity broker; the two
> break-glass accounts use sealed FIDO2 keys. The only tools allowed are the provider console,
> the cluster command-line client and the pipeline, as the runbook lists. Routine changes go
> through the pipeline with ISSO sign-off; a console session for diagnosis is announced in the
> operations channel, and the hourly drift scan reports any manual change to the ISSO, so the
> ISSO sees every session. The cluster audit log and the cloud account activity log record each
> session in the log store. Console sessions end at sign-out and expire after one hour; the
> cluster credentials are short-lived and expire with the session. The provider maintains the
> managed services itself in announced windows.
