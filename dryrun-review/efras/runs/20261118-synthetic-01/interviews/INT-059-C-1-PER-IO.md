---
interview_id: INT-059
run_id: 20261118-synthetic-01
task: C-1
persona: PER-IO
date: 2026-11-18
topics: [user community, access to maintenance data, outputs leaving the system]
---
# INT-059 — C-1 — PER-IO

### Q1 {#INT-059.Q1}
Asked of: PER-IO · Task: C-1
Who uses the system's outputs, and which user groups need which access to your maintenance
and readiness data?
**A1 {#INT-059.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#users]] [[product/architecture.md#identity]]
> Squadron maintenance personnel, about 2,400 of them, need their own squadron's readiness and
> forecasts and nothing else. Maintenance officers and chiefs, about 600, need air wing views,
> acknowledge forecasts and export reports. The fleet readiness analysts, about 40, are the only
> ones who see across the fleet and run ad hoc queries; I approve each `analyst` role myself,
> together with the user's supervisor. Senior leaders use the outputs but never log in: they get
> briefing slides by e-mail. Everyone who logs in is DoD military, civilian or a contractor
> working for the program; there are no foreign nationals or coalition users.

### Q2 {#INT-059.Q2}
Asked of: PER-IO · Task: C-1
How does information leave the system, and what do you require of each path?
**A2 {#INT-059.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#users]] [[product/conops.md#limitations]] [[product/data-flows.md#top]]
> Three ways: PDF and slide reports that officers export and e-mail to leaders, the analysts'
> de-identified data set exports, and the data scientists' training extract into the sandbox.
> Reports carry the CUI marking and go only to people with a need to know. The de-identified
> exports and training extract are not really de-identified today, because the DoD ID hash is
> unsalted; until release 1.6 I treat them as containing PII and require that they stay inside
> DoD systems. Nothing goes back to EMIS.

### Q3 {#INT-059.Q3}
Asked of: PER-IO · Task: C-1
Should the developer's data scientists and the cloud operations engineers see maintenance
data?
**A3 {#INT-059.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/conops.md#users]]
> The data scientists only get the training extract in the sandbox; I agreed to that for model
> building, and they have no access to production views. The cloud operations engineers can
> reach the database as administrators, which I accept because they operate it, but I expect
> their access to be logged and reviewed by the ISSO. Whether they are qualified for it is the
> ISSM's to answer.
