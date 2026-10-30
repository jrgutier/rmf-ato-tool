---
interview_id: INT-014
run_id: example-synthetic-01
task: P-12
persona: PER-IO
date: 2026-10-29
topics: [information types, provisional impact, ownership]
---
# INT-014 — P-12 — PER-IO

### Q1 {#INT-014.Q1}
Asked of: PER-IO · Task: P-12
**A1 {#INT-014.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#information]] [[product/data-flows.md#top]]
> The station handles five kinds of information: command and control data (routes, commands,
> telemetry), sensor video and still images, mission plans and flight logs, map and terrain
> data, and security management data (accounts, configuration, keys, audit records). All of it
> is unclassified in this program.

### Q2 {#INT-014.Q2}
Asked of: PER-IO · Task: P-12
**A2 {#INT-014.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#information]] [[product/conops.md#availability]] [[product/conops.md#mission]]
> Provisionally everything mission-related is moderate for confidentiality and integrity: a
> leak shows where the platoon is looking, and tampered commands could crash or misdirect a
> small unarmed aircraft, which is serious but not catastrophic because the aircraft flies its
> lost-link route home. Availability is moderate for command and control data, low for the rest,
> because a lost clip means flying the mission again. Map data is published, so low
> confidentiality but moderate integrity, since a wrong map misroutes the aircraft.

### Q3 {#INT-014.Q3}
Asked of: PER-IO · Task: P-12
**A3 {#INT-014.A3}** respondent: simulated · tag: SIMULATED · basis: [[ASM-006]]
> I own the mission information: command and control data, video and imagery, plans and logs.
> The map package belongs to the brigade geospatial cell that publishes it. Security management
> data belongs to the system owner and is kept by the ISSM.
