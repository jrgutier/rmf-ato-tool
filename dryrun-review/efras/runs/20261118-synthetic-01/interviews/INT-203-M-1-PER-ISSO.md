---
interview_id: INT-203
run_id: 20261118-synthetic-01
task: M-1
persona: PER-ISSO
date: 2027-02-01
topics: [unauthorized changes, drift scan, provider changes, reconciliation]
---
# INT-203 — M-1 — PER-ISSO

### Q1 {#INT-203.Q1}
Asked of: PER-ISSO · Task: M-1
How does monitoring look for unauthorized changes, and what did it find in the records you handed over?
**A1 {#INT-203.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/monitoring/cycle-2026-11.md#drift]] [[ART-CONMON]] [[ART-CMP]]
> The hourly drift scan (TOOL-02) compares the whole account with the version-controlled
> templates; I match every difference to an approved change request or the inventory, and an
> unmatched one is unauthorized. From 2026-11-01 to 2026-11-15 it ran 360 scans of the
> pre-production account and reported one event: on 2026-11-04 an engineer widened a security
> group from the console while troubleshooting. The scan flagged it within the hour, the
> pipeline reverted it the same hour, the cloud activity log named the engineer, and I counseled
> the team. My summary stops at 2026-11-15; I have not handed over a drift summary after that.

### Q2 {#INT-203.Q2}
Asked of: PER-ISSO · Task: M-1
What was the root cause of the 2026-11-04 change, and is it fixed?
**A2 {#INT-203.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/monitoring/cycle-2026-11.md#drift]] [[ART-CMP]]
> A process failure, not an attack: the cloud operations engineers' console role can still
> write security groups, so a change can be made outside the pipeline and the board, and the
> emergency change path in the CM plan was not used. Counseling does not remove the
> permission. The drift scan and the auto-revert worked as designed, so the exposure lasted under
> an hour and touched only pre-production with synthetic data. The lasting fix, a read-only
> console role with a break-glass path for emergencies, is not planned yet; it belongs with the
> configuration risk RSK-004.

### Q3 {#INT-203.Q3}
Asked of: PER-ISSO · Task: M-1
Which provider changes reached the system?
**A3 {#INT-203.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/monitoring/cycle-2026-11.md#threat]] [[product/monitoring/cycle-2026-11.md#vuln-scan]]
> One: after an ECSSP alert on the managed Kubernetes version, the provider patched the control
> plane on 2026-11-09 in its announced window. Provider-announced managed service patches are
> pre-approved in the CM plan; I logged it, the node scan of 2026-11-14 found no high or critical
> item, and the cluster kept working. The provider's authorization status did not change.
