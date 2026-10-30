---
interview_id: INT-020
run_id: agent-cold-start-resume
task: A-3
persona: PER-ISSO
date: 2026-10-30
topics: [account management evidence, audit event evidence, configuration scan evidence]
---
# INT-020 — A-3 — PER-ISSO

### Q1 {#INT-020.Q1}
Asked of: PER-ISSO · Task: A-3 · Control focus: ac-2
Show the account review record and explain how the `fieldtech` account is managed today.
**A1 {#INT-020.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#account-review]] [[product/conops.md#limitations]]
> Here is the 2026-09-12 review: 3 administrator and 2 auditor identity-service accounts, each
> matched to an approved access request; `esgadmin` sealed and unused since 2026-06; and the
> shared `fieldtech` account used by the 10 field technicians. Its password changes every 90
> days, not when someone leaves the team, and its sign-ins cannot be tied to a person; I
> referred that to the program office in the review record.

### Q2 {#INT-020.Q2}
Asked of: PER-ISSO · Task: A-3 · Control focus: au-2
What evidence shows the agreed events are generated and reach the SIEM?
**A2 {#INT-020.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#dt-2]] [[product/test-results.md#config-scan]]
> The event list signed with the CSSP on 2026-05-20, and the DT-2 results: sign-in, account
> change, configuration change and update installation events reached the SIEM within one
> minute on 12 of 12 units. The database audit rule for privileged activity was not a finding
> in the 2026-09-30 scan. My weekly review notes are on the ESG share.

### Q3 {#INT-020.Q3}
Asked of: PER-ISSO · Task: A-3 · Control focus: cm-6
What do the configuration scan and the nightly check show?
**A3 {#INT-020.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#config-scan]]
> The assessor-witnessed SRG/STIG scan on 2026-09-30 found the approved baseline on all 12
> units, with only the deviations in the STIG summary, and the TLS rule on the web server was not
> a finding. The nightly check reported no drift on any unit in August or September 2026.
