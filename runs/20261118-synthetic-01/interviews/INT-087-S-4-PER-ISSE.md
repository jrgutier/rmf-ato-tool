---
interview_id: INT-087
run_id: 20261118-synthetic-01
task: S-4
persona: PER-ISSE
date: 2026-11-18
topics: [access enforcement and least privilege by component]
---
# INT-087 — S-4 — PER-ISSE

### Q1 {#INT-087.Q1}
Asked of: PER-ISSE · Task: S-4 · Control focus: ac-3, ac-6
How does each allocated component enforce access and least privilege?
**A1 {#INT-087.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/test-results.md#dt-2]] [[product/test-results.md#pentest]]
> CMP-API checks the role and the squadron or air-wing scope on every request; users never reach
> the database directly, only through the API, as the Privacy Overlay suggests. DT-2 passed
> 212 crafted cross-squadron requests. CMP-REPORT repeats the scope check since release 1.5.1;
> pen test finding PT-1 showed it did not before, and the retest passed on 2026-11-10.
> CMP-SANDBOX reads only the training extract, never production tables. On CMP-K8S the
> workloads run under separate workload identities with namespace-scoped permissions, and
> engineers hold named console roles; only the four app-admins can change roles, and only the
> six engineers hold cluster privileges. Data scientists have no production privilege.

### Q2 {#INT-087.Q2}
Asked of: PER-ISSE · Task: S-4 · Control focus: ac-6, ac-17
Is anything in access enforcement still open?
**A2 {#INT-087.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#pentest]] [[product/conops.md#limitations]]
> The analyst export still yields re-identifiable data (limitation 1, PT-2), but that is a
> de-identification flaw, not an access enforcement one: only `analyst` holders get the export.
> The sandbox egress wildcard (PT-3) was narrowed on 2026-11-03 and waits on retest; it is a
> boundary control matter. Nothing else is open in AC.
