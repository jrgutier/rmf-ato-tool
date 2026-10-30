---
interview_id: INT-016
run_id: agent-skeleton
task: S-4
persona: PER-DEV
date: 2026-10-30
topics: [flaw remediation, update bundles, local authentication enforcement]
---
# INT-016 — S-4 — PER-DEV

### Q1 {#INT-016.Q1}
Asked of: PER-DEV · Task: S-4 · Control focus: si-2
How are flaws identified, fixed, tested and released?
**A1 {#INT-016.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#updates]] [[product/architecture.md#configuration]]
> We track vulnerabilities in the OS, collector, console and database and fix them in a
> signed monthly update bundle. Each bundle is built by the same pipeline as the hardened image
> and tested on our reference units before release; the units verify the bundle signature
> before installing it. Bundles change the approved baseline, so each one goes through the
> RSSPO configuration control board.

### Q2 {#INT-016.Q2}
Asked of: PER-DEV · Task: S-4 · Control focus: si-2
How quickly do fielded units get each bundle, and what is the plan to close the gap?
**A2 {#INT-016.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/test-results.md#vuln-scan]]
> Units are updated by technicians at the quarterly site visit, so a bundle can wait up to
> about three months, longer than the 30-day period. At the 2026-09-30 scan, `esg-north-01`
> and `esg-ridge-01` ran the 2026-07 bundle, 63 days old, with 4 high and 9 medium
> vulnerabilities that later bundles fix; the other 10 units were current. Release 2.2, planned
> for 2026-12, adds remote update over the uplink so bundles can be installed within 30 days.

### Q3 {#INT-016.Q3}
Asked of: PER-DEV · Task: S-4 · Control focus: ia-2
What does the console code enforce for local sign-in?
**A3 {#INT-016.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/test-results.md#dt-2]]
> Five failed local sign-ins lock the account for 30 minutes, and every console session locks
> after 15 minutes idle; DT-2 passed both. The local store holds only `esgadmin` and
> `fieldtech`; per-technician accounts with smart-card login are in release 2.3.
