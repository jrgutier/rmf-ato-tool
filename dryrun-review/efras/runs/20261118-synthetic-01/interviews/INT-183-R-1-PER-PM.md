---
interview_id: INT-183
run_id: 20261118-synthetic-01
task: R-1
persona: PER-PM
date: 2026-12-14
topics: [package submission, executive summary issues, package sharing with information owners and interconnected systems]
---
# INT-183 — R-1 — PER-PM

### Q1 {#INT-183.Q1}
Asked of: PER-PM · Task: R-1
When, to whom and by whom is the authorization package submitted?
**A1 {#INT-183.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-173.A1]] [[INT-180.A5]] [[product/conops.md#program]]
> I submit it myself as system owner, to the AO through the AODR, today, 2026-12-14, once the
> CISO's quality review of the assessment report is in. It holds the security plan with its
> family files and plan records, the assessment plan and report, the POA&M of 24 items, the
> PIA as it stands (a draft under privacy office review) and the DIAS. I ask for the decision
> before the 2027-02-01 deployment, once the before-authorization items dated by 2027-01-25 are
> worked off.

### Q2 {#INT-183.Q2}
Asked of: PER-PM · Task: R-1
Which risk management issues should the executive summary put in front of the AO?
**A2 {#INT-183.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-180.A1]] [[INT-180.A2]] [[INT-180.A4]] [[INT-181.A3]] [[product/conops.md#limitations]]
> Five. First, the re-identifiable exports and the PIA that cannot be approved until they are
> fixed: no production maintainer data until both close. Second, the two high vulnerabilities in
> the report container and the two PostgreSQL STIG settings, all waiting on the factory's late
> base image. Third, leavers keep access because nobody tells the account manager. Fourth, the
> EMIS exchange runs on an interim e-mail approval with no signed agreement. Fifth, recovery from
> a regional outage is unproven: no failover test and no tabletop until 2027-02. And the AO has
> to decide on the break-glass FIDO2 deviation, which we cannot fix.

### Q3 {#INT-183.Q3}
Asked of: PER-PM · Task: R-1
Who besides the AO receives the package: the information owners, and the owners of each interconnected system?
**A3 {#INT-183.A3}** respondent: simulated · tag: SIMULATED · basis: [[INT-047.A2]] [[product/architecture.md#interconnections]] [[product/architecture.md#leveraged]] [[product/stakeholders.md#governance]]
> The information owner of the maintenance and readiness data gets the whole package. The owners
> of the seven connected systems behind CONN-01 to CONN-07 (the cloud access point, the cloud
> region, the identity broker, EMIS, the supply status service, the software factory and the
> CSSP) get it through eMASS visibility on the same day, 2026-12-14, because each of them carries
> part of the risk or depends on our side of the connection. No organization receives EFRAS
> under reciprocity: we deploy only to our own production account.
