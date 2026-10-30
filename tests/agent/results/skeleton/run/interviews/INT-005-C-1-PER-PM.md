---
interview_id: INT-005
run_id: agent-skeleton
task: C-1
persona: PER-PM
date: 2026-10-30
topics: [system identity, lifecycle, mission, interconnections, leveraged authorizations]
---
# INT-005 — C-1 — PER-PM

### Q1 {#INT-005.Q1}
Asked of: PER-PM · Task: C-1
Do you confirm the proposed name and acronym in the product profile, and does the system go by any other name?
**A1 {#INT-005.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/profile.yaml]] [[product/conops.md#mission]]
> I confirm both: the system is the Example Sensor Gateway, ESG for short. It has no other
> official name or alias in program documents.

### Q2 {#INT-005.Q2}
Asked of: PER-PM · Task: C-1
Has the system been registered, and what identifier should the package use?
**A2 {#INT-005.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#program]]
> Registration has not been completed yet, so I have no registry identifier to give you. Use a
> placeholder until the component registry assigns one.

### Q3 {#INT-005.Q3}
Asked of: PER-PM · Task: C-1
What is the system's lifecycle state and what is deployed today?
**A3 {#INT-005.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#program]]
> We are in engineering and manufacturing development, so the system is under development.
> Twelve pre-production units sit at test sites and feed a test instance of IODS; none has
> carried operational alarm traffic. We plan to field 60 units after an authorization decision.

### Q4 {#INT-005.Q4}
Asked of: PER-PM · Task: C-1
In your words, what is the mission and what does the system do end to end?
**A4 {#INT-005.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#mission]] [[product/architecture.md#components]]
> ESG gives the security operations center a near-real-time picture of perimeter intrusion and
> environmental conditions at remote sites. Each unit collects readings from up to 40 sensor
> nodes over the field radio, validates them, buffers up to 7 days locally and forwards them to
> IODS. It senses and forwards only; it makes no decisions and actuates nothing.

### Q5 {#INT-005.Q5}
Asked of: PER-PM · Task: C-1
Which systems does ESG connect to, under what agreements, and whose controls does it inherit?
**A5 {#INT-005.A5}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#interconnections]] [[product/architecture.md#leveraged]]
> ESG sends telemetry to IODS under an interconnection agreement signed 2026-04-02; IODS has
> its own ATO. We sign in through the installation ICAM service under a service agreement. We
> inherit controls from two authorized providers: the Installation Network Enclave, ATO
> 2025-11-20, which also covers the ICAM service, and the Installation CSSP, ATO 2026-01-30.
> IODS is a partner we exchange data with, not a provider we inherit from.
