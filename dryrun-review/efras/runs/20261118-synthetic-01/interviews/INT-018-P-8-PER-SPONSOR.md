---
interview_id: INT-018
run_id: 20261118-synthetic-01
task: P-8
persona: PER-SPONSOR
date: 2026-11-18
topics: [missions, business functions, mission/business processes, disruption impact, mission critical functions, external dependents, criticality]
---
# INT-018 — P-8 — PER-SPONSOR

### Q1 {#INT-018.Q1}
Asked of: PER-SPONSOR · Task: P-8
**A1 {#INT-018.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#mission]] [[product/conops.md#program]]
> The capability needs statement my directorate approved for readiness analytics, under which
> the program entered execution on 2026-03-02, says what this service supports. The mission is
> naval aviation readiness: keeping aircraft mission-capable. The business function is
> aircraft maintenance and readiness management. The processes are three: daily readiness
> reporting for squadron, air wing and fleet; part failure forecasting so maintenance officers
> order parts early; and fleet readiness analysis by the fleet analysts, including the
> de-identified data sets they export.

### Q2 {#INT-018.Q2}
Asked of: PER-SPONSOR · Task: P-8
**A2 {#INT-018.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#mission]] [[product/conops.md#availability]]
> None of these is a mission critical or mission essential function inside the system. The
> service is decision support only: it does not write to the maintenance information system,
> order parts or change aircraft status, and if it is down squadrons fall back to the
> maintenance system's own reports. Readiness reporting then slips by a day or more, but no
> aircraft is grounded. I rate the disruption impact of each process Low: limited adverse
> effect, with a manual fallback.

### Q3 {#INT-018.Q3}
Asked of: PER-SPONSOR · Task: P-8
**A3 {#INT-018.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#availability]] [[product/conops.md#users]]
> Readiness reporting tolerates an outage of up to 72 hours; past that, fleet reporting goes
> back to manual reports. Forecasting can wait a week, since it looks 30 days ahead. Fleet
> analysis can wait a week too. Senior leaders depend on readiness reporting through the
> briefing slides they receive by e-mail; they hear of an outage through the fleet readiness
> directorate's daily readiness brief, which notes when the data is late.

### Q4 {#INT-018.Q4}
Asked of: PER-SPONSOR · Task: P-8
**A4 {#INT-018.A4}** respondent: simulated · tag: SIMULATED · basis: [[INT-018.A1]] [[product/data-flows.md#main]]
> In order of what matters most to the mission: daily readiness reporting first, then part
> failure forecasting, then fleet analysis. Readiness reporting depends on the nightly pull from
> the maintenance information system and the supply status service; without the maintenance
> data there is nothing to report. Sign-in through the enterprise identity broker underpins all
> three.
