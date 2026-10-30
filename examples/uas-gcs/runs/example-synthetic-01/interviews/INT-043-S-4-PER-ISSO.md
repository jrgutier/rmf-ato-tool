---
interview_id: INT-043
run_id: example-synthetic-01
task: S-4
persona: PER-ISSO
date: 2026-10-29
topics: [cp family, contingency plan, spare station, backup, recovery]
---
# INT-043 — S-4 — PER-ISSO

### Q1 {#INT-043.Q1}
Asked of: PER-ISSO · Task: S-4 · Control focus: cp-1, cp-2, cp-2.1, cp-2.3, cp-2.8, cp-3, cp-4, cp-4.1
What does the contingency plan cover, and how is it trained and tested?

**A1 {#INT-043.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#availability]] [[ART-ORG-CONTEXT]]
> Policy comes from the Component cybersecurity program. The plan is a short station
> contingency plan, started in S-4 as ART-CP: when a station fails, the platoon draws a spare
> kit from brigade stock and has mission planning and flight control running within 4 hours;
> the critical assets are the workstation, the GDT and the router. It is coordinated with the
> brigade's continuity and the enclave's incident response plans and reviewed annually. Today
> only the summary exists; the full plan, the role-based training in the station swap, and the
> first tabletop test with the brigade are planned before fielding.

### Q2 {#INT-043.Q2}
Asked of: PER-ISSO · Task: S-4 · Control focus: cp-6, cp-6.1, cp-6.3, cp-7, cp-7.1, cp-7.2, cp-7.3, cp-8, cp-8.1, cp-8.2, cp-9, cp-9.1, cp-9.5, cp-9.8, cp-10, cp-10.2
How are backups, alternate sites and links handled, and how is a station recovered?

**A2 {#INT-043.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#availability]] [[product/architecture.md#network]] [[product/architecture.md#updates]] [[product/architecture.md#physical]]
> Spare kits are held in brigade stock away from the platoons and can be reached by ground
> transport; the spare station is the alternate processing site and is owned by the unit, so no
> outside service provider or priority agreement is involved. The maintainer takes an encrypted
> backup of the workstation configuration and mission data to platoon-controlled media after
> each bundle install and weekly, checks it by test-restoring on one station each quarter, and
> sends a copy with the brigade spare stock. The aircraft link and the uplink are each single
> paths per station; when the uplink drops, the station keeps flying and products queue for
> transfer, and a failed GDT or router is covered by swapping in the spare kit. The enclave
> carries the uplink under its own telecom priority arrangements. Recovery is a reimage from
> the signed bundle plus the backup; queued products resume transfer when the link returns.
