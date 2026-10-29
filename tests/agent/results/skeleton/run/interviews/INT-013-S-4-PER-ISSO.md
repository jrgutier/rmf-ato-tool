---
interview_id: INT-013
run_id: agent-skeleton
task: S-4
persona: PER-ISSO
date: 2026-10-29
topics: [account management, shared account, event logging, log review]
---
# INT-013 — S-4 — PER-ISSO

### Q1 {#INT-013.Q1}
Asked of: PER-ISSO · Task: S-4 · Control focus: ac-2
**A1 {#INT-013.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/conops.md#users]]
> The console allows three kinds of account: identity-service accounts mapped to the `admin` or
> `auditor` role by group claim, one break-glass local account `esgadmin`, and the shared local
> `fieldtech` account. Nothing else. A remote user files an ESG access request; I approve it, and
> the identity service's account workflow creates the account and the group membership. I am the
> account manager on the ESG side.

### Q2 {#INT-013.Q2}
Asked of: PER-ISSO · Task: S-4 · Control focus: ac-2
**A2 {#INT-013.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/test-results.md#account-review]]
> I review the console account list against the access request records every quarter. The last
> record is dated 2026-09-12: 3 administrators and 2 auditors, all approved; `esgadmin` unused
> since 2026-06; `fieldtech` used by the 10 field technicians. Break-glass use is logged and
> reported, and the envelope sits in the program office safe.

### Q3 {#INT-013.Q3}
Asked of: PER-ISSO · Task: S-4 · Control focus: ac-2
**A3 {#INT-013.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/test-results.md#account-review]]
> The gap is `fieldtech`. Its password is shared by the team and changed every 90 days, not when
> a technician leaves the team, and its sign-ins cannot be tied to a person. I referred that to
> the program office at the September review. The fix is per-technician local accounts with
> smart-card login in release 2.3, planned for 2027-03. Until then I cannot claim individual
> accountability for on-site privileged actions.

### Q4 {#INT-013.Q4}
Asked of: PER-ISSO · Task: S-4 · Control focus: ac-2
**A4 {#INT-013.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/architecture.md#logging]]
> For removal: when someone leaves, the identity service disables their account and the group
> claim goes with it, so they lose console access; I confirm at the next quarterly review. Account
> use is monitored through the sign-in and account-change events that go to the SIEM, and I read
> the ESG report weekly.

### Q5 {#INT-013.Q5}
Asked of: PER-ISSO · Task: S-4 · Control focus: au-2
**A5 {#INT-013.A5}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]] [[product/test-results.md#dt-2]]
> The OS audit daemon, the collector and the console log sign-in success and failure, account
> changes, privilege use, configuration changes, update installation, service start and stop, and
> radio pairing. That list was agreed with the CSSP on 2026-05-20 and is reviewed every year.
> Events reach the SIEM within one minute (DT-2 passed on 12 of 12 units) and stay on the unit
> for 30 days.
