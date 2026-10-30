---
interview_id: INT-010
run_id: example-synthetic-01
task: P-10
persona: PER-DEV
date: 2026-10-29
topics: [item list, versions, firmware]
---
# INT-010 — P-10 — PER-DEV

### Q1 {#INT-010.Q1}
Asked of: PER-DEV · Task: P-10
**A1 {#INT-010.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/hw-sw-inventory.md#items]] [[product/architecture.md#components]]
> The configuration-item list INV-001 to INV-010 is complete for the 2.3.0 release. Every
> station gets the same items; the air module INV-009 is one per aircraft. Nothing else is
> installed on the station beyond what the workstation image INV-002 contains.

### Q2 {#INT-010.Q2}
Asked of: PER-DEV · Task: P-10
**A2 {#INT-010.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/hw-sw-inventory.md#items]] [[product/architecture.md#components]]
> The flight control, video and planner applications all run on the workstation image. The GDT
> firmware 5.1.8 includes the GDT's management web service, so that service is part of INV-007,
> not a separate item. The router runs its vendor OS 11.2.

### Q3 {#INT-010.Q3}
Asked of: PER-DEV · Task: P-10
**A3 {#INT-010.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/hw-sw-inventory.md#items]]
> The map package INV-010 has no fixed version: it is loaded per mission from published map
> products, so we track the package, not a version.
