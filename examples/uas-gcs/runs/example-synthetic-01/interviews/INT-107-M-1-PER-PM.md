---
interview_id: INT-107
run_id: example-synthetic-01
task: M-1
persona: PER-PM
date: 2026-10-29
topics: [change requests, security impact analysis, significant change]
---
# INT-107 — M-1 — PER-PM

### Q1 {#INT-107.Q1}
Asked of: PER-PM · Task: M-1 · Control focus: cm-3, cm-4
Which changes to the station have been requested or made since the authorization, and who
analyzed their security impact?

**A1 {#INT-107.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#updates]] [[product/test-results.md#vuln-scan]] [[INT-064.A1]]
> Two change requests are open in the first monitoring cycle, and no change has been installed
> outside them. CR-2026-10 is the integrator's quarterly 2026-10 bundle with the operating
> system and router patches for the three medium scan findings; it is approved for the six test
> stations but is not installed until the post-install scan is scheduled, so we do not run an
> unscanned bundle. CR-2026-12 is the 2026-12 bundle carrying ground data terminal firmware
> 5.2.1, still in regression testing. The ISSO wrote the security impact analysis for both and
> the ISSM reviewed it before the board met.

### Q2 {#INT-107.Q2}
Asked of: PER-PM · Task: M-1 · Control focus: significant change, ongoing authorization
Is any planned change significant enough to go back to the AO before it is made?

**A2 {#INT-107.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[ART-CONMON]]
> Neither bundle is: both patch existing items and change no boundary, interface or data flow.
> Two later changes are significant and I will bring them to the AO through the ISSM before
> they reach a station: release 2.4 (planned 2027-02) replaces the shared `gcsmaint` account
> with per-maintainer accounts and offline CAC sign-in, which changes how maintainers
> authenticate; and the planner replacement for release 3.0, which changes a component and
> must start again at the boundary and system description. Neither has a change request yet.
