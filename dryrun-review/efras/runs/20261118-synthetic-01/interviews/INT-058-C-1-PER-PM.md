---
interview_id: INT-058
run_id: 20261118-synthetic-01
task: C-1
persona: PER-PM
date: 2026-11-18
topics: [system identity, lifecycle, version, ownership, mission and functions, sites, interconnections and agreements]
---
# INT-058 — C-1 — PER-PM

### Q1 {#INT-058.Q1}
Asked of: PER-PM · Task: C-1
Do you confirm the official name and acronym proposed in the product profile, and does the
system go by any other name?
**A1 {#INT-058.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/profile.yaml]] [[product/conops.md#mission]]
> I confirm both: the official name is "Example Fleet Readiness Analytics Service" and the
> acronym is EFRAS. It has no other official name or alias; squadrons call it "the readiness
> dashboard", but that is not a name we register or use in documents.

### Q2 {#INT-058.Q2}
Asked of: PER-PM · Task: C-1
Which identifier does the system carry: the eMASS record or something else?
**A2 {#INT-058.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-056.A1]] [[ART-REG]] [[ART-ORG-CONTEXT]]
> The system identifier the Component uses in its risk management program and its governance
> lists is EFRAS itself. EFRAS-0001 is the number of our record in the Component eMASS
> instance; that is the registry record, not a second name for the system. Use EFRAS as the
> system identifier and keep the eMASS record number on the registration record.

### Q3 {#INT-058.Q3}
Asked of: PER-PM · Task: C-1
What is the lifecycle state, the current version and its release date, and the acquisition
phase?
**A3 {#INT-058.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#program]] [[product/profile.yaml]]
> Under development. The version we are seeking authorization for is release 1.5, the minimum
> viable capability release; it was cut and deployed to pre-production on 2026-10-27, and it runs
> there for three pilot squadrons, about 140 users, on synthetic data. We are on the software
> acquisition pathway and entered its execution phase on 2026-03-02. In the five-phase model the
> templates ask for, the closest fit is Production and Deployment, which is what our profile
> proposes: we are producing releases and must deploy MVCR to an operational environment by
> 2027-02-01. Release 1.5.2 follows on 2026-12-10 for the base image fix, and 1.6 on 2027-01-15.

### Q4 {#INT-058.Q4}
Asked of: PER-PM · Task: C-1
Who owns and who operates the system, and which environment does this authorization cover?
**A4 {#INT-058.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#program]] [[product/conops.md#users]] [[product/architecture.md#boundary]]
> The government owns it: the Aviation Readiness Software Program Office (ARSPO), under the
> naval aviation PEO, and I am the system owner. Day-to-day operation of the cloud account,
> cluster, database and pipelines is done by ERST, our contractor team, under the program's
> direction; the ISSO and ISSM are government. So it is government-owned, contractor-operated.
> The authorization covers the production environment, the program-owned production cloud
> account. The pre-production account is not part of it.

### Q5 {#INT-058.Q5}
Asked of: PER-PM · Task: C-1
What does the system do, for whom, and where are its parts?
**A5 {#INT-058.A5}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#mission]] [[product/conops.md#environment]] [[product/architecture.md#physical]]
> Every night it pulls maintenance actions, part removals and aircraft status from EMIS, joins
> them with supply status and shows squadron, air wing and fleet readiness dashboards; a
> forecast job predicts likely part failures in the next 30 days so officers can order early.
> It is decision support only: it never writes back to EMIS or orders parts. All of it runs in
> the Example GovCloud IL4 region in our own account. We own no building or hardware; the only
> program-held equipment is the ERST privileged access workstations, which sit in the program's
> controlled office space. Users reach it over NIPRNet from their squadrons and staffs.

### Q6 {#INT-058.Q6}
Asked of: PER-PM · Task: C-1
What does the system connect to, under which agreements, and who signed them?
**A6 {#INT-058.A6}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#interconnections]] [[product/conops.md#limitations]]
> Three connections to other systems. EMIS sends us its nightly extract; the memorandum of
> agreement with the EMIS program is drafted and still in legal review, and the connection runs
> on an interim e-mail approval from the EMIS ISSM; I expect signature by 2026-12-31. EMIS holds
> an ATO of 2025-04-22, valid to 2028-04-22. The supply status service is under a service-level
> agreement signed on 2026-06-30 by me and the supply status service's program manager; that
> service has an ATO of 2024-11-05. The identity broker onboarded us on 2026-05-12 under the
> enterprise onboarding approval, signed by the broker's service owner; it runs under an
> enterprise service ATO. All three are DoD Component systems, not mission partners. I do not
> have the names of the other systems' AOs to hand; they are in their ATO letters, which the
> ISSM holds.
