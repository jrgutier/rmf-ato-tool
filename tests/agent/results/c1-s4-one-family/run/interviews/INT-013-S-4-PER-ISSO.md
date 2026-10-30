---
interview_id: INT-013
run_id: agent-c1-s4-one-family
task: S-4
persona: PER-ISSO
date: 2026-10-30
topics: [account lifecycle, reviews, shared and emergency accounts, monitoring]
---
# INT-013 — S-4 — PER-ISSO

### Q1 {#INT-013.Q1}
Asked of: PER-ISSO · Task: S-4
**A1 {#INT-013.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/test-results.md#account-review]]
> I approve every ESG access request; the identity service's workflow then creates, changes or
> disables the remote account and its group claim, which the console maps to `admin` or
> `auditor`. Every quarter I compare the console account list and roles with the request records;
> the last review was 2026-09-12. Departures and high-risk cases go to the identity service, which
> disables the account at once. Access procedures follow the Component access control policy.

### Q2 {#INT-013.Q2}
Asked of: PER-ISSO · Task: S-4
**A2 {#INT-013.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/test-results.md#account-review]]
> Local accounts are managed by hand on the console. `fieldtech` is shared by about ten
> technicians, its password changes every 90 days, and its sign-ins cannot be tied to a person,
> so I cannot remove one technician without changing the password for all. Per-technician
> accounts with smart-card login come in release 2.3, planned for 2027-03. The break-glass
> `esgadmin` account is sealed in the program office safe; its use is logged and reported to me,
> but nothing disables it automatically after use: I reseal and change it by hand.

### Q3 {#INT-013.Q3}
Asked of: PER-ISSO · Task: S-4
**A3 {#INT-013.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]]
> Sign-ins, account changes, privilege use and configuration changes go to the CSSP SIEM within one
> minute; the CSSP correlates them for atypical use and remote-access anomalies, and I review the
> ESG report weekly.
