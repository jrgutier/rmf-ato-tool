---
interview_id: INT-017
run_id: example-synthetic-01
task: P-14
persona: PER-ISSM
date: 2026-10-29
topics: [threat events, vulnerabilities, likelihood and impact]
---
# INT-017 — P-14 — PER-ISSM

### Q1 {#INT-017.Q1}
Asked of: PER-ISSM · Task: P-14
**A1 {#INT-017.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[ASM-003]] [[product/data-flows.md#top]]
> I applied the organization's five threat themes to the station: jamming or spoofing of the
> aircraft link, capture of a kit in the field, malicious code arriving on maintenance media, a
> compromised commercial component or integrator build, and patches and log review slipping
> while disconnected. I used the SP 800-30 qualitative five-level scales and the Table I-2
> matrix, and rated within the organization's tolerance.

### Q2 {#INT-017.Q2}
Asked of: PER-ISSM · Task: P-14
**A2 {#INT-017.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/architecture.md#identity]] [[product/architecture.md#logging]]
> The station-specific weaknesses are the three the program disclosed: the mission planner has
> no STIG and its manual hardening is unassessed, with vendor support ending 2027-06; the shared
> `gcsmaint` account means maintenance actions cannot be tied to a person; and the GDT firmware
> has a published crash vulnerability in its management service with the 5.2.1 fix still in
> regression testing. Add the GDT's single vendor administrator password, and that the planner
> and GDT logs are local only and never forwarded.

### Q3 {#INT-017.Q3}
Asked of: PER-ISSM · Task: P-14
**A3 {#INT-017.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-BND]] [[product/architecture.md#network]] [[product/architecture.md#physical]]
> What helps: the GDT management service listens only on the isolated station segment, the
> uplink is deny-by-default, the aircraft link is encrypted with per-mission keys and never
> routed to the uplink, disks are encrypted, cases carry tamper seals, update bundles are signed,
> and the enclave provides boundary protection, IDS and log collection. None of the risks is
> high after those; the shared account and the GDT firmware are the top two.
