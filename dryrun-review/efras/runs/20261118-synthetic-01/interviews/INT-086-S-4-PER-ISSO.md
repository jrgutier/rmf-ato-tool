---
interview_id: INT-086
run_id: 20261118-synthetic-01
task: S-4
persona: PER-ISSO
date: 2026-11-18
topics: [account management, access policy and procedures, remote access]
---
# INT-086 — S-4 — PER-ISSO

### Q1 {#INT-086.Q1}
Asked of: PER-ISSO · Task: S-4 · Control focus: ac-2
How are accounts requested, approved, created, reviewed and removed, and how does the privacy
training rule from S-2 work in practice?
**A1 {#INT-086.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/test-results.md#account-review]] [[product/test-results.md#dt-2]] [[INT-074.A3]]
> The account types are the five application roles (viewer, officer, analyst, app-admin,
> auditor), named cloud console roles, two sealed break-glass console accounts and workload
> service identities; shared, guest and temporary accounts are prohibited. A user requests a role
> in the Component's access request system; the supervisor approves, and the information owner
> also approves `analyst`. I provision the group, which the identity broker asserts. Squadron
> scoping is an attribute of the assertion. Accounts unused for 35 days are disabled
> automatically (tested in DT-2). I review every role assignment quarterly; the last review was
> 2026-10-06, 141 accounts, two removed. For the privacy training rule, the Component training
> system sends me a monthly list of users whose annual privacy training has lapsed and I disable
> those accounts; the 24-hour notices for departures and need-to-know changes come from the
> personnel out-processing checklist to me and the account managers. Account use is monitored
> through the sign-in and role-change events in the log pipeline.

### Q2 {#INT-086.Q2}
Asked of: PER-ISSO · Task: S-4 · Control focus: ac-1
Which access control policy and procedures govern EFRAS, who owns them and how often are they
reviewed?
**A2 {#INT-086.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]]
> The Component's access control policy applies at organization level; the ISSM owns the
> system-level access control procedures, which sit in the EFRAS security operations runbook in
> the program's document repository and are given to the ERST engineers, the app-admins and me.
> The ISSM reviews the procedures annually and after a significant change or an incident; the
> Component reviews its policy annually.

### Q3 {#INT-086.Q3}
Asked of: PER-ISSO · Task: S-4 · Control focus: ac-17
What kinds of remote access exist and how is each authorized?
**A3 {#INT-086.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/architecture.md#identity]] [[product/conops.md#users]]
> Every user is remote. Users reach the web front end over NIPRNet through the access point on
> 443 only, with CAC at the identity broker. Cloud operations engineers reach the private cluster
> API and the console only from ERST privileged access workstations through the provider's
> privileged access path, after CAC sign-in. Each type is written in the runbook with its
> connection requirements and is authorized by the ISSM before anyone uses it. The break-glass
> accounts use a FIDO2 key, so they are still two-factor, but not CAC.
