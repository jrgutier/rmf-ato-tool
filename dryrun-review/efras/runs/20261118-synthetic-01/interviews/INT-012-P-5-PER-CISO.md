---
interview_id: INT-012
run_id: 20261118-synthetic-01
task: P-5
persona: PER-CISO
date: 2026-11-18
topics: [common control providers, controls offered, provider authorizations, assessment of common controls, how systems inherit]
---
# INT-012 — P-5 — PER-CISO

### Q1 {#INT-012.Q1}
Asked of: PER-CISO · Task: P-5
**A1 {#INT-012.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[ASM-006]]
> My common control list names four providers that business systems in the cloud may inherit
> from: the Example GovCloud IL4 region, under its DoD provisional authorization of 2024-09-18;
> the Example Enterprise Cloud Access Point, authorized 2025-01-10; the Example Software
> Factory, authorized 2025-10-01; and the Example Cybersecurity Service Provider, whose
> services are delivered under its own ATO and a service agreement, the agreement with ARSPO
> dated 2026-04-01. I designate each as a common control provider on the list; none is
> appointed by this program.

### Q2 {#INT-012.Q2}
Asked of: PER-CISO · Task: P-5
**A2 {#INT-012.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-012.A1]] [[ASM-006]]
> Each provider's common controls were assessed by an assessor the provider arranged and my
> office accepted as qualified: the provisional authorization assessment by an accredited
> third-party assessment organization, the access point and the CSSP by their Component
> assessment teams, and the software factory by its own independent assessment team. Each
> package, its security plan, assessment report and POA&M, was approved by the AO accountable
> for those controls before it was published to inheriting programs, and ARSPO received each
> package at onboarding. Providers report compliance status monthly through the Component
> inheritance portal, the CSSP through its monthly service report.

### Q3 {#INT-012.Q3}
Asked of: PER-CISO · Task: P-5
**A3 {#INT-012.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[INT-012.A2]]
> Deficiencies: the software factory's package carries an open POA&M item for the delayed
> hardened base image release, which affects programs waiting on it; the other three packages
> have no open deficiency that touches the controls offered. A system inherits by citing the
> provider in its SSP, configuring its own side, and recording the leveraged authorization.
