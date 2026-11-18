---
interview_id: INT-122
run_id: 20261118-synthetic-01
task: S-4
persona: PER-CCB
date: 2026-11-18
topics: [configuration control board, approved baseline, preapproved and emergency changes, change records]
---
# INT-122 — S-4 — PER-CCB

### Q1 {#INT-122.Q1}
Asked of: PER-CCB · Task: S-4 · Control focus: cm-3 (configuration management plan)
Who sits on the board and who chairs it? How often does it meet, what triggers an emergency meeting, what is its quorum and decision rule, and when does a change go above it?
**A1 {#INT-122.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-094.A1]] [[product/architecture.md#configuration]] [[product/stakeholders.md#governance]]
> The product manager chairs the EFRAS configuration control board. Members: the ISSM, the
> ISSE, the ERST technical lead and the user representative; the ISSO attends every meeting
> as the deployment sign-off authority, and the Component privacy office and the CSSP attend
> as guests when a change touches PII or monitoring. We meet monthly. An emergency meeting is
> called by the chair or the ISSM, by phone or chat within one working day, for an emergency
> patch or a change made to restore service. Quorum is the chair (or the ISSM as alternate),
> the ISSE and the ERST technical lead. We decide by
> consensus; if there is none the chair decides, and the ISSM can stop any change that raises
> security risk until the AO's office has seen it. A change goes above the board, to the AO
> through the ISSM, when the security impact analysis rates it significant: a new
> interconnection, a new type of data, a change to the boundary, to the identity path or to
> the privacy safeguards in the PIA or SORN. Changes that also touch the software factory or
> the cloud region are coordinated with their own boards; ours decides only for EFRAS.

### Q2 {#INT-122.Q2}
Asked of: PER-CCB · Task: S-4 · Control focus: cm-2, cm-3, cm-6
Which changes are preapproved, how are emergency changes handled afterwards, and which baseline and deviations did the board approve?
**A2 {#INT-122.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-093.A1]] [[product/architecture.md#updates]] [[product/test-results.md#stig-scan]]
> Preapproved: the monthly worker-node image roll to the provider's newest hardened image,
> routine dependency updates that pass every pipeline gate, and provider-announced managed
> service patches. They still go through a pull request, the gates and ISSO sign-off, and are
> listed in the next board minutes. An emergency patch (deployable within 48 hours under the
> same gates) is analyzed, tested and approved retroactively at the next board meeting, where
> the ISSE presents the impact analysis and the test results. The board approved the release
> 1.5 baseline: the infrastructure templates and release manifest at tag 1.5.0, with the
> Kubernetes and PostgreSQL STIG deviations the ISSM approved in the STIG summary (the
> provider-managed control plane checks and the four database settings the managed service
> does not expose). Change requests, analyses, decisions and minutes live in the program's
> issue tracker and repository.
