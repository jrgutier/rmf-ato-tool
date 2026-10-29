---
interview_id: INT-023
run_id: agent-skeleton
task: A-3
persona: PER-ISSO
date: 2026-10-29
topics: [account review evidence, shared account, log review evidence, configuration check evidence]
---
# INT-023 — A-3 — PER-ISSO

### Q1 {#INT-023.Q1}
Asked of: PER-ISSO · Task: A-3 · Control focus: ac-2
**A1 {#INT-023.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#account-review]]
> Here is the 2026-09-12 quarterly review record. I compared the console account list with the
> access request records: 3 administrator and 2 auditor identity-service accounts, each with an
> approved request on file; the break-glass account `esgadmin`, unused since 2026-06; and the
> shared local account `fieldtech`. The previous review was in June; the record lists both dates.

### Q2 {#INT-023.Q2}
Asked of: PER-ISSO · Task: A-3 · Control focus: ac-2
**A2 {#INT-023.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/test-results.md#account-review]]
> About 10 field technicians use `fieldtech` on the maintenance port. They all know the same
> password, which I change every 90 days. When a technician leaves the team, the password is not
> changed until the next 90-day rotation; I have no record of an out-of-cycle change. The audit
> records show `fieldtech`, never a person, so I cannot tell you who did what on site. My review
> record refers that to the program office.

### Q3 {#INT-023.Q3}
Asked of: PER-ISSO · Task: A-3 · Control focus: ac-2
**A3 {#INT-023.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[INT-013.A1]]
> When a remote user leaves, the identity service disables the account or removes the group claim,
> and I confirm at the next quarterly review that the account is gone from the console list. The
> September review found no stale identity-service account. The `esgadmin` credential is sealed in
> the program office safe; the seal log shows no use since June.

### Q4 {#INT-023.Q4}
Asked of: PER-ISSO · Task: A-3 · Control focus: au-2
**A4 {#INT-023.A4}** respondent: simulated · tag: SIMULATED · basis: [[INT-013.A5]] [[product/architecture.md#logging]]
> I keep the CSSP-agreed event list dated 2026-05-20 and my weekly SIEM report notes; the last
> twelve weekly reports are on file. Each report shows sign-in, account-change, configuration-change
> and update events from all twelve units. The first annual event-list review with the CSSP is due
> in 2027-05; none has happened yet because the list is less than a year old.

### Q5 {#INT-023.Q5}
Asked of: PER-ISSO · Task: A-3 · Control focus: cm-6
**A5 {#INT-023.A5}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#config-scan]] [[INT-019.A2]]
> The nightly configuration check reports drift to the SIEM; there was no drift alert in August or
> September 2026. The deviations are approved in the RSSPO configuration control board minutes,
> and the 2026-09-30 SRG/STIG scan was witnessed by one of your assessors. I have the scan export
> and the board minutes for you.
