---
interview_id: INT-033
run_id: 20261118-synthetic-01
task: P-13
persona: PER-IO
date: 2026-11-18
topics: [maintenance data life cycle, forecasts and reports, release rules]
---
# INT-033 — P-13 — PER-IO

Respondent: the fleet maintenance data steward.

### Q1 {#INT-033.Q1}
Asked of: PER-IO · Task: P-13
**A1 {#INT-033.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#mission]] [[product/data-flows.md#main]]
> The maintenance and readiness data is collected nightly from EMIS, processed and stored, used in
> the dashboards and the forecast job, and disseminated only inside the reports and dashboards.
> EFRAS never writes it back to EMIS. My release rules allow export only by maintenance officers
> and fleet analysts, and only of their own unit unless they hold the analyst role.

### Q2 {#INT-033.Q2}
Asked of: PER-IO · Task: P-13
**A2 {#INT-033.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#users]] [[INT-032.A1]]
> Forecasts are created by the forecast job and reports by the report service; both are stored,
> viewed, exported and, for briefing slides, e-mailed to senior leaders outside the system. Once a
> slide leaves by e-mail it follows the recipient's CUI handling, not EFRAS's. Inside EFRAS the
> forecasts are kept with the maintenance data and purged on the same 5-year window.
