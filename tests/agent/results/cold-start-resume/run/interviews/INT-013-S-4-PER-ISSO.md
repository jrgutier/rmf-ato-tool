---
interview_id: INT-013
run_id: agent-cold-start-resume
task: S-4
persona: PER-ISSO
date: 2026-10-30
topics: [account management, event logging, account reviews]
---
# INT-013 — S-4 — PER-ISSO

### Q1 {#INT-013.Q1}
Asked of: PER-ISSO · Task: S-4 · Control focus: ac-2
How are console accounts defined, approved, created and removed?
**A1 {#INT-013.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/conops.md#limitations]]
> Allowed account types are identity-service accounts for remote administrators and auditors,
> mapped to the `admin` and `auditor` roles by group claim, one sealed break-glass account
> `esgadmin`, and today the shared local `fieldtech` account. I am the account manager. A user
> gets access only after I approve an ESG access request; the identity service's account
> workflow then creates the account and the group claim, and removal of the claim removes
> access. Break-glass use is logged and reported to me.

### Q2 {#INT-013.Q2}
Asked of: PER-ISSO · Task: S-4 · Control focus: ac-2
How are accounts monitored and reviewed, and what is not in place?
**A2 {#INT-013.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#account-review]] [[product/conops.md#limitations]]
> I review the console account list quarterly against the access request records; the last
> review was 2026-09-12. Sign-ins go to the SIEM, so account use is monitored. The gap is
> `fieldtech`: ten technicians share it, its password changes only every 90 days rather than when
> someone leaves the team, and their sign-ins cannot be attributed to a person. Per-technician
> accounts with smart-card login come in release 2.3, planned for 2027-03.

### Q3 {#INT-013.Q3}
Asked of: PER-ISSO · Task: S-4 · Control focus: au-2
Which events are logged, how was the list agreed, and how often is it reviewed?
**A3 {#INT-013.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]] [[product/test-results.md#dt-2]]
> The OS audit daemon, the collector and the console log sign-in success and failure, account
> changes, privilege use, configuration changes, update installation, service start and stop,
> and radio pairing. We agreed that list with the CSSP on 2026-05-20 as what an incident
> investigation needs, and we review it annually. Events reach the SIEM within one minute; DT-2
> confirmed that on all 12 units. The CSSP correlates them; I review the ESG report weekly. The
> event set is complete, but `fieldtech` events name the shared account, not a person.
