---
interview_id: INT-077
run_id: example-synthetic-01
task: A-3
persona: PER-ISSO
date: 2026-10-29
topics: [ia assessment evidence, ir assessment evidence, ma assessment evidence]
---
# INT-077 — A-3 — PER-ISSO

### Q1 {#INT-077.Q1}
Asked of: PER-ISSO · Task: A-3 · Control focus: ia-2, ia-4, ia-5, ia-12
Show me the records for identifiers and authenticators: who has which account, how it was requested, and how the shared accounts are handled.

**A1 {#INT-077.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#account-review]]
> Here is the 2026-09-08 review: 14 CAC accounts, each with a supervisor-signed request in my
> folder, 6 sealed break-glass envelopes unopened. The shared `gcsmaint` account is on every
> workstation and router and 5 maintainers know its password; I change it every 60 days, last
> on 2026-09-30. The GDT vendor administrator password was set at installation and has never
> been changed. Nobody authenticates individually before using `gcsmaint`, and there is no
> token or card for maintenance access. Fixes are planned in release 2.4 (2027-02).

### Q2 {#INT-077.Q2}
Asked of: PER-ISSO · Task: A-3 · Control focus: ia-11, ia-5.13, ia-6
Demonstrate re-authentication, credential masking and cached sign-in expiry on a station.

**A2 {#INT-077.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]]
> On station 3 the screen locked at 15 minutes and asked for the CAC PIN; the elevation prompt
> asked for the PIN again. PINs and passwords show as dots on the workstation, router and GDT
> sign-in screens. Station 6 has been off the directory since 2026-10-14; today, after 15 days,
> it refused the cached CAC sign-in until it reconnected.

### Q3 {#INT-077.Q3}
Asked of: PER-ISSO · Task: A-3 · Control focus: ir-2, ir-3, ir-4, ir-8, ir-9
What incident response training, tests and plan exist, and what happened in past incidents?

**A3 {#INT-077.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]]
> Nobody has had station incident response or spillage training yet, and the plan has never
> been tested; the tabletop with the brigade and CSSP is not scheduled. The plan is still the
> summary in ART-IRP, with no breach-handling section. There have been no incidents on the
> test stations. The isolation and reimage steps were walked through on station 5 during the
> 2026-10 restore, and I keep the forensic image procedure and the Component spillage
> procedure in the station binder. Planner and GDT logs are not forwarded, so during an
> incident I would read them on the device; `gcsmaint` actions cannot be tied to a person for
> an insider case.

### Q4 {#INT-077.Q4}
Asked of: PER-ISSO · Task: A-3 · Control focus: ma-2, ma-3, ma-5, ma-6
Show the maintenance records, tool inventory and authorized maintainer list.

**A4 {#INT-077.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#physical]]
> The maintenance log for each station lists every action since 2026-07, with date and task,
> but the sign-in shows `gcsmaint`, not the maintainer; the person is only named for
> scheduled work. The diagnostic kit is on the baseline inventory, its case seals were checked
> and logged at every setup, and the kit stays in the platoon's locked case. The authorized
> maintainer list has the 5 names, signed by me. The station 5 swap from a spare kit took under
> 3 hours. The 2026-10 quarterly bundle, which also updates the tools, was installed on all six
> stations after its signature check, and media are scanned at the kiosk first.
