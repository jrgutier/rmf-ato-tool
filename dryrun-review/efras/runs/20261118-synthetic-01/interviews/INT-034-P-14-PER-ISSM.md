---
interview_id: INT-034
run_id: 20261118-synthetic-01
task: P-14
persona: PER-ISSM
date: 2026-11-18
topics: [threat sources, threat products, vulnerabilities, connections, providers, suppliers, risk model, team]
---
# INT-034 — P-14 — PER-ISSM

### Q1 {#INT-034.Q1}
Asked of: PER-ISSM · Task: P-14
**A1 {#INT-034.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[product/conops.md#information]]
> Four threat sources matter. First, nation-state cyber actors after aggregated readiness and
> logistics data: high capability, high intent, and moderate targeting of EFRAS itself, since it
> is one of several readiness systems. Second, criminal actors and phishers after the maintainer
> personal data: moderate capability, moderate intent, low targeting. Third, insiders with
> privileged access, ERST engineers and app administrators, through error far more than malice:
> I rate the accidental insider with a moderate range of effects. Fourth, structural failure of
> the cloud region or a provider service: moderate range of effects.

### Q2 {#INT-034.Q2}
Asked of: PER-ISSM · Task: P-14
**A2 {#INT-034.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[product/architecture.md#leveraged]]
> Threat information comes from the Component's naval aviation cyber threat assessment, an
> Intelligence Community product the Component intelligence office briefed to us on 2026-07-15,
> and from ECSSP threat alerts through 2026-11. We consulted the Component intelligence office's
> cyber threat analyst on 2026-08-04 and the program's security officer for counterintelligence.
> Vulnerability information is the pipeline and scan results of 2026-10-20 and 2026-10-22, the
> penetration test of 2026-10-27 to 2026-10-31 and the known limitations list. Impact
> information is the business impact analysis and the information owners' impact levels.

### Q3 {#INT-034.Q3}
Asked of: PER-ISSM · Task: P-14
**A3 {#INT-034.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/test-results.md#pentest]] [[product/test-results.md#pipeline-1-5]] [[product/test-results.md#stig-scan]]
> The vulnerabilities to carry are the disclosed ones: re-identifiable exports (PT-2, limitation
> 1), the two high vulnerabilities in example-imagelib (limitation 2), no signed EMIS agreement
> (limitation 3), the untested regional failover (limitation 4), the break-glass accounts without
> CAC (limitation 5), 90-day audit retention (limitation 6), the unapproved PIA (limitation 7),
> two program-fixable PostgreSQL STIG items, and PT-3, the sandbox egress wildcard narrowed on
> 2026-11-03 with the retest still pending. PT-1 is fixed and retested, so it is history, not a
> current weakness. Predisposing conditions: dependence on one cloud region, and a fleet-wide
> user population of about 3,000 reaching the service over NIPRNet.

### Q4 {#INT-034.Q4}
Asked of: PER-ISSM · Task: P-14
**A4 {#INT-034.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#interconnections]] [[product/architecture.md#leveraged]]
> Connections: EMIS is the riskiest, moderate, because personal data arrives over it under an
> interim approval only. Supply, the identity broker, the access point, ECSSP and the factory are
> low; the cloud region is low too because its provisional authorization covers what we inherit.
> Every provider gives assurance through its own authorization, so trust is sufficient for all
> of them; the software factory's open POA&M is the one I watch. Suppliers: ERST for our code,
> the factory for the base image, the cloud provider for every managed service, and the open
> source projects behind example-imagelib and the web framework. The imagelib supply chain is the
> moderate one; the rest are low.

### Q5 {#INT-034.Q5}
Asked of: PER-ISSM · Task: P-14
**A5 {#INT-034.A5}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]]
> We use the Component model: SP 800-30 semi-quantitative, five levels from very low to very
> high, threat-oriented, likelihood combining initiation and adverse impact by Table G-5, risk by
> Table I-2, a one-year horizon. Borderline values were rounded up when the event touches personal
> data, down otherwise, and the uncertainty is written with each rating. The team was me as lead,
> the ERST security engineer and the ISSO, with the privacy officer for privacy risk; contact is
> the ARSPO ISSM mailbox, issm.arspo@example.mil (fictional). We assessed on 2026-11-18. No part of
> the assessment was tailored down for resources.

### Q6 {#INT-034.Q6}
Asked of: PER-ISSM · Task: P-14
**A6 {#INT-034.A6}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#interconnections]] [[product/architecture.md#leveraged]] [[product/hw-sw-inventory.md#items]]
> For the low connections I have no open weakness to name, but they are not free of risk: EFRAS
> leans on services it does not run and cannot see inside. Users get in only through the access
> point, sign in only through the identity broker, releases come only from the factory, monitoring
> sits with ECSSP, and supply data arrives from a system we do not control. Call that a predisposing
> condition of moderate pervasiveness. The same goes for ERST's code and the web framework: every
> image ERST builds pulls in third-party and open-source components whose maintainers we do not
> control. No weakness is open in them today, so that is a condition too, moderate pervasiveness.
