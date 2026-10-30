---
interview_id: INT-102
run_id: example-synthetic-01
task: R-3
persona: PER-AODR
date: 2026-10-29
topics: [risk responses, residual risk, operator notification]
---
# INT-102 — R-3 — PER-AODR

### Q1 {#INT-102.Q1}
Asked of: PER-AODR · Task: R-3 · Control focus: RSK-001 to RSK-009
Is each risk's response reflected in the POA&M, and what residual risk remains?

**A1 {#INT-102.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-POAM]] [[ART-RAR]]
> Acting for the AO under delegation: every risk has a mitigate response and every one of its
> findings has a POA&M item with dated milestones and resources, so no item needs changing. The
> residual risk after the interim measures stays moderate until Release 2.4 is fielded on
> 2027-03-31; RSK-003 stays moderate until firmware 5.2.1 and the rescan by 2027-01-15. The
> planner library flaws without a vendor fix will not be mitigated before the planner is
> replaced, so that residual part of RSK-003 goes to the AO for explicit acceptance at R-4,
> conditioned on keeping the planner on the internal network only and loading data only through
> signed bundles.

### Q2 {#INT-102.Q2}
Asked of: PER-AODR · Task: R-3 · Control focus: operators
Which operators must be told of potential impacts, and what do they need to know?

**A2 {#INT-102.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-RAR]]
> The fielding units and the enclave operators. They need to know that maintenance actions
> cannot be attributed until Release 2.4, that planner and GDT activity is not monitored while
> disconnected, that the GDT management service can be crashed from the station segment, and
> that incident and contingency response rests on draft plans until 2026-12-18. The ISSM sends
> the notice with the decision and repeats it in each monthly POA&M report.
