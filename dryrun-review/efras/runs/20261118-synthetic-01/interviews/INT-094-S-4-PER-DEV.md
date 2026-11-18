---
interview_id: INT-094
run_id: 20261118-synthetic-01
task: S-4
persona: PER-DEV
date: 2026-11-18
topics: [configuration change control in the pipeline]
---
# INT-094 — S-4 — PER-DEV

### Q1 {#INT-094.Q1}
Asked of: PER-DEV · Task: S-4 · Control focus: cm-3
Which changes are configuration-controlled, and how does a change get approved and recorded?
**A1 {#INT-094.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#configuration]] [[product/architecture.md#updates]] [[INT-074.A3]]
> Every change to code, images, infrastructure templates or cluster configuration is controlled;
> nothing reaches the cluster except through the pipeline. A change is a pull request, reviewed
> by a second engineer with a security and privacy impact note, then it passes the gates (static,
> dependency, image and dynamic scans, policy checks), and the ISSO signs off before deploy.
> Major releases and any change touching safeguards in the PIA or SORN go to the configuration
> control board, which also meets monthly. The pull request, gate results and sign-off stay in
> the repository and pipeline records; we keep them for the life of the system plus one year. The
> hourly drift scan catches anyone who goes around the pipeline.
