---
interview_id: INT-152
run_id: 20261118-synthetic-01
task: A-3
persona: PER-ISSO
date: 2026-12-01
topics: [access control procedures, account records, leaver timing test, remote access records]
---
# INT-152 — A-3 — PER-ISSO

### Q1 {#INT-152.Q1}
Asked of: PER-ISSO · Task: A-3 · Control focus: ac-1
Show me the access control procedures you work from, who has them, and the record of their last review.
**A1 {#INT-152.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-SSP]] [[ART-ORG-CONTEXT]]
> The procedures are the access control chapter of the EFRAS security operations runbook in the
> program document repository. The document control page shows version 2.1, reviewed and
> re-issued by the ISSM on 2026-06-15 after the move to release 1.5, with the previous annual
> review on 2025-10-20. The repository's access list gives read access to the six ERST cloud
> operations engineers, the four application administrators and me. The runbook cites the
> Component access control policy and its own purpose, scope, roles and responsibilities. I have
> no record of the Component's policy review other than its issue date on the policy itself.

### Q2 {#INT-152.Q2}
Asked of: PER-ISSO · Task: A-3 · Control focus: ac-2
Show me the account records: the requests and approvals for a sample of accounts, the inactivity disable setting, and the last account review.
**A2 {#INT-152.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#account-review]] [[product/test-results.md#dt-2]] [[product/architecture.md#identity]]
> Every one of the accounts you drew has a request in the Component access request system with
> the supervisor's approval, and the analyst accounts also carry the information owner's
> approval. Roles come only from the broker group I provision; there are no shared, guest or
> temporary accounts. The 35-day inactivity disable is a setting in the API's account job, and
> DT-2 tested it. The quarterly review of 2026-10-06 covered 141 user accounts, 4 app-admins,
> 6 console roles, the 2 sealed break-glass accounts and 9 service identities; sign-in and
> role-change events in the log store show account use, and the weekly report lists role changes.

### Q3 {#INT-152.Q3}
Asked of: PER-ISSO · Task: A-3 · Control focus: ac-2 (leaver timing, PRC-004)
For the leaver-timing test: for each departed user in the sample, when did you learn of the departure, and when was the account disabled?
**A3 {#INT-152.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#account-review]] [[ASM-020]]
> The two users who left a pilot squadron before the 2026-10-06 review were not disabled when
> they left: I found them at the review and removed them then. Their out-processing checklists
> were completed by the squadron, but the checklist step that notifies the EFRAS account manager
> was not reached; it relies on the squadron administrative office sending me an e-mail, and
> neither e-mail exists. For the other eight leavers you drew, the checklists show the departure
> date but no notification time to me, and the API logs only the removal; I cannot show that any
> of them reached me within 24 hours. The pilot squadrons do not yet feed departures to EFRAS
> automatically.

### Q4 {#INT-152.Q4}
Asked of: PER-ISSO · Task: A-3 · Control focus: ac-17
Show me where each type of remote access is documented and the record that the ISSM authorized it before use.
**A4 {#INT-152.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/architecture.md#identity]]
> The runbook's remote access section documents the two types, user web access through the
> access point and engineer access from the privileged access workstations, with the port, the
> TLS versions and the sign-in path for each, and the ISSM's authorization memo of 2026-03-10
> approves both before the pilot squadrons were connected. No other remote path exists: the
> cluster API is private and no node has a public address.
