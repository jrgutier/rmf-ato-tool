---
interview_id: INT-153
run_id: 20261118-synthetic-01
task: A-3
persona: PER-DEV
date: 2026-11-20
topics: [access enforcement, export scoping fix, privileged roles, workload identities]
---
# INT-153 — A-3 — PER-DEV

### Q1 {#INT-153.Q1}
Asked of: PER-DEV · Task: A-3 · Control focus: ac-3
Show me where the API and the report service enforce role and scope, the DT-2 scoping results and the PT-1 fix and retest.
**A1 {#INT-153.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#dt-2]] [[product/test-results.md#pentest]] [[product/architecture.md#identity]]
> The API's authorization middleware reads the role and the squadron or air-wing scope from the
> session and filters every query; there is no database access for users. DT-2 ran 212 crafted
> requests against it and all were refused. The report service took the scope from the export
> request until release 1.5.1 (2026-11-07); since then it calls the same scope check as the API,
> and the red team's retest on 2026-11-10 passed. The sandbox reads only the training extract
> bucket; its workload identity has no grant on the production tables.

### Q2 {#INT-153.Q2}
Asked of: PER-DEV · Task: A-3 · Control focus: ac-6
Which identities hold privileges on the cluster, the database and in the application, and how are workload permissions scoped?
**A2 {#INT-153.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#account-review]] [[product/architecture.md#identity]]
> In the application, only the four app-admins can change roles. On the cluster, the six ERST
> engineers hold named console roles; nobody else has a cluster role. Each of the nine service
> identities is bound to its own namespace with the permissions its workload needs and no
> cluster-wide grant. The database has the application's role, the ingest role and the sealed
> break-glass role. The three data scientists have no production role, only the sandbox.
