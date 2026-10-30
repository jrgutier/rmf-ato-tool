---
interview_id: INT-098
run_id: example-synthetic-01
task: A-6
persona: PER-PM
date: 2026-10-29
topics: [remediation releases, resources, dates, interim mitigations]
---
# INT-098 — A-6 — PER-PM

### Q1 {#INT-098.Q1}
Asked of: PER-PM · Task: A-6 · Control focus: shared-account and log findings
When does release 2.4 field, and what covers the gap until then?

**A1 {#INT-098.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-094.A1]] [[INT-094.A2]]
> Release 2.4 (per-maintainer accounts, offline CAC sign-in, planner and GDT log forwarding) is
> funded in the current program budget and fields to all six stations by 2027-03-31: build
> complete 2027-01-29, developmental test 2027-02-26. In the interim the GDT administrator
> password gets a named custodian and a change by 2026-11-30, and the ISSO exports and reviews
> planner and GDT logs at every reconnect starting 2026-11-16.

### Q2 {#INT-098.Q2}
Asked of: PER-PM · Task: A-6 · Control focus: FND-054, FND-062, FND-063, FND-021, FND-061, FND-068, FND-059
And the vulnerabilities and the application hardening?

**A2 {#INT-098.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-094.A2]] [[INT-097.A1]]
> GDT firmware 5.2.1 goes into the 2026-12 bundle, installed by 2026-12-18, with a rescan of all
> six stations by 2027-01-15. The planner library findings have no vendor fix; we will ask for
> risk acceptance at R-3 and keep the internal-network-only restriction. The developer runs the
> planner, flight control and video SRG checks and writes the planner security guide by
> 2027-01-29 with existing contract staff.

### Q3 {#INT-098.Q3}
Asked of: PER-PM · Task: A-6 · Control focus: FND-058, FND-069
The planner end-of-support items cannot meet the 180-day period. What is the plan?

**A3 {#INT-098.A3}** respondent: simulated · tag: SIMULATED · basis: [[INT-094.A3]]
> Selection of the release 3.0 planner by 2027-01-29, integration in release 3.0 and fielding
> by 2027-06-30, the day support ends. That is about two months past the 180-day period; a
> replacement cannot be selected, integrated and tested faster, so I request a milestone
> extension. Release 3.0 needs new funding, which I am requesting in the 2027 budget review.
