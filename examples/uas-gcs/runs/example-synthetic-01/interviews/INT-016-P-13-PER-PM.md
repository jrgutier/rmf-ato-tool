---
interview_id: INT-016
run_id: example-synthetic-01
task: P-13
persona: PER-PM
date: 2026-10-29
topics: [information life cycle, retention, disposition]
---
# INT-016 — P-13 — PER-PM

### Q1 {#INT-016.Q1}
Asked of: PER-PM · Task: P-13
**A1 {#INT-016.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/data-flows.md#mission]] [[product/architecture.md#network]]
> Command data is created in flight control from the imported plan and sent over the aircraft
> link; telemetry comes back the same way and is shown and logged. Video is collected through
> the GDT, recorded and clipped in the video application, and once the commander releases a
> product it goes to the intelligence system or queues until the uplink is up.

### Q2 {#INT-016.Q2}
Asked of: PER-PM · Task: P-13
**A2 {#INT-016.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]] [[product/architecture.md#updates]]
> Audit records stay on the station for 90 days and are forwarded to the enclave collector.
> Maps and updates arrive on removable media. Our retention practice: recordings and plans are
> deleted from the station once transferred and verified, at the latest when the kit is reset
> between missions; disks are sanitized before a kit leaves the program. Mission keys are zeroized
> after each mission.
