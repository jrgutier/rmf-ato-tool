---
interview_id: INT-022
run_id: example-synthetic-01
task: C-1
persona: PER-PM
date: 2026-10-29
topics: [system identity, lifecycle state, mission and functions, sites, interconnections]
---
# INT-022 — C-1 — PER-PM

### Q1 {#INT-022.Q1}
Asked of: PER-PM · Task: C-1
**A1 {#INT-022.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/profile.yaml]] [[ASM-009]]
> I confirm the proposed name "Example Tactical UAS Ground Control Station" and the acronym
> "ETGCS" unchanged. We use no other name for it. Until the registry assigns a separate system
> number, use the registration record reference ETGCS-REG-SIM-0001 as the system identifier.

### Q2 {#INT-022.Q2}
Asked of: PER-PM · Task: C-1
**A2 {#INT-022.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#program]]
> The system is under development: we are in EMD with six pre-production stations at the test
> range, connected only to a test instance of the brigade network. Fielding of 48 stations to 16
> platoons follows Milestone C and an authorization decision.

### Q3 {#INT-022.Q3}
Asked of: PER-PM · Task: C-1
**A3 {#INT-022.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#mission]] [[product/architecture.md#components]]
> Each station plans a route, uploads it, commands one Kestrel-X aircraft over the
> line-of-sight link, records and clips sensor video and hands mission products to the brigade
> network. It carries no weapons and makes no targeting decisions. If a station fails, the
> aircraft flies its lost-link route home.

### Q4 {#INT-022.Q4}
Asked of: PER-PM · Task: C-1
**A4 {#INT-022.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#interconnections]] [[product/architecture.md#leveraged]]
> We have two connections: IC-1 to the brigade intelligence system, whose interconnection
> agreement is still an unsigned draft that we will sign before fielding, and IC-2 to the
> Brigade Tactical Network Enclave under its connection approval process. We inherit enclave
> boundary protection, intrusion detection, the directory, log collection and incident response
> support from the enclave's ATO of 2025-05-30. The intelligence system only receives our data;
> we inherit nothing from it.
