---
interview_id: INT-005
run_id: agent-skeleton
task: C-1
persona: PER-PM
date: 2026-10-29
topics: [system identity, lifecycle state, mission and functions, sites and quantities, interconnections]
---
# INT-005 — C-1 — PER-PM

### Q1 {#INT-005.Q1}
Asked of: PER-PM · Task: C-1
**A1 {#INT-005.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/profile.yaml]] [[product/conops.md#mission]]
> I confirm the official name as proposed in the profile, "Example Sensor Gateway", and the
> acronym "ESG". The program uses no other name for it, so there are no aliases.

### Q2 {#INT-005.Q2}
Asked of: PER-PM · Task: C-1
**A2 {#INT-005.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#program]]
> Registration has not issued an identifier yet; the registration task is not part of this
> cycle and nothing in our material gives one. Use "ESG-001" as a placeholder until the
> registry assigns the real identifier.

### Q3 {#INT-005.Q3}
Asked of: PER-PM · Task: C-1
**A3 {#INT-005.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#program]]
> We are in engineering and manufacturing development under the major capability acquisition
> pathway. Twelve pre-production units sit at test sites feeding a test instance of IODS; no
> unit has carried operational alarm traffic. So the state is under development. Fielding of
> 60 units follows the authorization decision.

### Q4 {#INT-005.Q4}
Asked of: PER-PM · Task: C-1
**A4 {#INT-005.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#mission]] [[product/architecture.md#components]]
> The mission is near-real-time perimeter intrusion and environmental sensing for the SOC at
> remote sites. Each unit collects readings from up to 40 field sensor nodes over the field
> radio, validates and buffers them, and forwards them to IODS. It senses and forwards only; it
> decides nothing and actuates nothing.

### Q5 {#INT-005.Q5}
Asked of: PER-PM · Task: C-1
**A5 {#INT-005.A5}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#interconnections]] [[product/architecture.md#leveraged]]
> We connect to IODS under the interconnection agreement signed 2026-04-02, and to the ICAM
> service under the installation service agreement. We inherit from two separately authorized
> providers: the Installation Network Enclave, ATO 2025-11-20, whose authorization also covers
> the ICAM service, and the CSSP, ATO 2026-01-30. IODS is a partner we send data to, not a
> provider we inherit controls from. For control-level detail on what we inherit, ask the ISSM.
