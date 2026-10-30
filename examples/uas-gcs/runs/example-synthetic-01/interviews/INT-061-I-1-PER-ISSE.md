---
interview_id: INT-061
run_id: example-synthetic-01
task: I-1
persona: PER-ISSE
date: 2026-10-29
topics: [engineering methods, deviations from the plan, third-party components]
---
# INT-061 — I-1 — PER-ISSE

### Q1 {#INT-061.Q1}
Asked of: PER-ISSE · Task: I-1 · Control focus: sa-8, pl-8
Was the approved plan built as written, or did implementation deviate from it?

**A1 {#INT-061.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/test-results.md#dt-1]]
> The 2.3.0 build follows the approved plan. DT-1 confirmed the planned behavior: CAC sign-in,
> lockout and screen lock, the keyed aircraft link, lost-link return and the router's port
> filtering. I know of no change to a planned control; the open items are the three disclosed
> limitations, which the plan already marks partial.

### Q2 {#INT-061.Q2}
Asked of: PER-ISSE · Task: I-1 · Control focus: cm-6, sa-22, sr-3
What assurance do you have for the third-party components without a benchmark?

**A2 {#INT-061.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/test-results.md#vuln-scan]]
> Little for the mission planner: the SRG-based hardening is recorded but unassessed, its
> bundled library has two medium findings with no vendor fix date, and vendor support ends
> 2027-06. For the ground data terminal firmware we rely on the vendor's signed releases and
> keep the management service reachable only from the station's internal network until 5.2.1
> is fielded.
