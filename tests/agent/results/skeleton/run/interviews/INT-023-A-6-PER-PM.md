---
interview_id: INT-023
run_id: agent-skeleton
task: A-6
persona: PER-PM
date: 2026-10-30
topics: [remediation plan per finding, releases and funding, interim mitigations]
---
# INT-023 — A-6 — PER-PM

### Q1 {#INT-023.Q1}
Asked of: PER-PM · Task: A-6 · Control focus: si-2
How and when will the program fix FND-003 (update latency on fielded units), and what covers the gap until then?
**A1 {#INT-023.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-SAR]] [[product/architecture.md#updates]] [[product/conops.md#limitations]]
> Release 2.2 adds remote update over the uplink and is funded in the current development
> contract; we plan to field it by 2026-12-15 and to have every unit on it by 2026-12-31.
> Until then I am funding out-of-cycle site visits: the field team updates esg-north-01 and
> esg-ridge-01 by 2026-11-14, and from now on any unit whose bundle is about to pass 30 days
> gets a visit. Release 2.2 is past the 30-day installation period because it needs the
> uplink change and a regression test cycle; the visits keep every unit inside the period
> in the meantime.

### Q2 {#INT-023.Q2}
Asked of: PER-PM · Task: A-6 · Control focus: ac-2, ia-2
How and when will the program fix FND-001 and FND-002 (the shared `fieldtech` account)?
**A2 {#INT-023.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-SAR]] [[product/conops.md#limitations]]
> One fix closes both: release 2.3 brings per-technician local accounts with smart-card login
> on the maintenance port and removes `fieldtech`. It needs card readers for the 10 field
> technicians' laptops and about two developer-months, both in the FY27 budget line, so the
> earliest realistic date is 2027-03-31. Until then the ISSM's site-visit sign-in log ties each
> `fieldtech` session to a named technician, and the password is changed whenever a
> technician leaves the team. I accept that this date is past what I would like and will
> report progress to the AO monthly.
